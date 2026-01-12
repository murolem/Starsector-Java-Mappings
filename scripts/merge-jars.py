#!/usr/bin/env python3

# Original Author: mogwailabs
# Modified version of the original jarjarbigs.py.

from zipfile import ZipFile

import sys
import shutil
import os
import argparse
import zipfile

from pathlib import Path

def scan_directory_for_file_ext(root: str, file_ext: str, shallow: bool = False) -> list[str]:
    if not file_ext.startswith("."):
        file_ext = "." + file_ext
    ext_lower = file_ext.lower()

    result = list()
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if Path(filename).suffix.lower() == ext_lower:
                result.append(dirpath + filename)

        if shallow:
            break

    return result

def scan_directory_for_jars(directory, shallow: bool = False):
    archives = scan_directory_for_file_ext(directory, "jar", shallow=shallow)
    archives.extend(scan_directory_for_file_ext(directory, "war", shallow=shallow))
    archives.extend(scan_directory_for_file_ext(directory, "ear", shallow=shallow))
    return archives

def truncate_path_if_exceeds_length(path_str: str, max_length: int) -> str:
    path_str = os.path.normpath(path_str)
    parts = path_str.split(os.sep)
    
    for i, part in enumerate(parts):
        if len(part) <= max_length:
            continue
            
        # truncate from left
        parts[i] = part[-max_length:]
        
    return os.sep.join(parts)

def merge_archive_into_archive(archive: ZipFile, target_archive: ZipFile) -> None:
    print("[+] Processing " + archive.filename)
    if args.logfile:
        log_file = open(args.logfile[0], "a")

    target_archive_names = target_archive.namelist()

    added_counter = 0
    for info in archive.infolist():
        if (
            info.is_dir()
            or not info.filename.endswith(".class")
            or info.filename.startswith("META-INF" + os.sep)
        ):
            continue

        if info.filename in target_archive_names:
            print("[-] Encountered a class file with duplicate path: \n    Already written to: " + info.filename)
            # exit(1)

        contents_bytes = archive.read(info.filename)
        target_archive.writestr(info.filename, data=contents_bytes)
        added_counter += 1

        # Log the file
        if args.logfile:
            log_file.write(info.filename)

    print(f"[+] added {added_counter} class files")

    if args.logfile:
        log_file.close()

def create_jar_archive(source_directory, archive_name):
    print("[+] Creating jar archive " + archive_name)
    shutil.make_archive(archive_name, 'zip', source_directory)
    os.rename(archive_name + ".zip", archive_name)


if __name__ == '__main__':
    print("--- merge-jars.py 0.2 (MODIFIED), original by MOGWAI LABS GmbH --------------------------------------\n")

    parser = argparse.ArgumentParser(
        description="merge-jars.py - create a huge jar file from existing jar/war/ear files")
    parser.add_argument('source', help="source directory with jar/war/ear files")
    parser.add_argument('destination', help="destination jar file")
    parser.add_argument('--only', help="jar whitelist", nargs='*')
    parser.add_argument('-l', '--logfile', nargs=1, default=None,
                        help='Create a log file which jar contains which classes')

    args = parser.parse_args()

    if sys.version_info[0] < 3:
        print("[-] Please use Python3 (for zip64 support)")
        exit(2)

    if not os.path.isdir(args.source):
        print("[-] source does not exists or is not a directory")
        exit(1)
    elif os.path.isdir(args.destination):
        print("[-] destination is a directory")
        exit(1)

    archives = scan_directory_for_jars(args.source, shallow=True)
    if args.only:
        archives = [el for el in archives if os.path.basename(el) in args.only]

    if len(archives) == 0:
        print("[-] no JARs found")
        exit(1)

    merged_archive = zipfile.ZipFile(args.destination, "w")
    for archive in archives:
        merge_archive_into_archive(zipfile.ZipFile(archive, "r"), merged_archive)
