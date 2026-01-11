#!/usr/bin/env python3

# Author: mogwailabs
# Modified version of the original jarjarbigs.py. Modifications include:
# - Scanning for JARs is now shallow.
# - Long class filenames are truncated to system filename limit.

import tempfile
import sys
import shutil
import os
import argparse
import zipfile
from builtins import str, list, enumerate, len, print, FileExistsError, OSError, exit, open
from glob import glob

from os import listdir
from os.path import isfile, join
from pathlib import Path

log_entries = []
MAX_PATH_NAME_LEN = os.pathconf('/', 'PC_NAME_MAX')

def scan_directory_shallow_files_with_ext(dirpath: str, ext: str) -> list[str]:
    ext_lower = ext.lower()
    result = list()
    for root, dirs, filenames in os.walk(dirpath):
        for filename in filenames:
            if Path(filename).suffix.lower() == ext_lower:
                result.append(filename)
        break   #prevent descending into subfolders since files are enumerated first

    return result

def scan_directory_shallow(directory):
    archives = scan_directory_shallow_files_with_ext(directory, "jar")
    archives.extend(scan_directory_shallow_files_with_ext(directory, "war"))
    archives.extend(scan_directory_shallow_files_with_ext(directory, "ear"))
    return archives

def truncate_path_if_exceeds_name_limit(path_str: str) -> str:
    path_str = os.path.normpath(path_str)
    parts = path_str.split(os.sep)
    
    for i, part in enumerate(parts):
        if len(part) <= MAX_PATH_NAME_LEN:
            continue
            
        # truncate from left
        parts[i] = part[-MAX_PATH_NAME_LEN:]
        
    return os.sep.join(parts)

def copy_class_files(archive, source, destination):
    class_files = [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*.class'))]

    if arguments.logfile:
        log_file = open(arguments.logfile[0], "a")

    for class_file in class_files:
        current_path = os.path.dirname(class_file)[len(source):]
        current_path = current_path.replace('WEB-INF/classes/', '')
        current_path = current_path.replace('BOOT-INF/classes/', '')
        current_file = os.path.basename(class_file)
        destination_path = destination + current_path
        if not destination_path.endswith("/"):
            destination_path += "/"

        # check if the path exists, if not, create it
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # Copy the class file to the new destination
        shutil.copyfile(class_file, destination_path + current_file)

        # Log the file
        if arguments.logfile:
            log_file.write("{}: {}\n".format(os.path.basename(archive), current_path[1:] + current_file))

    if arguments.logfile:
        log_file.close()


def copy_xml_files(archive, source, destination):
    xml_files = [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*.xml'))]
    xml_files += [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*.properties'))]

    for xml_file in xml_files:
        current_path = os.path.dirname(xml_file)[len(source):]
        current_file = os.path.basename(xml_file)
        destination_path = destination + '/' + os.path.basename(archive) + current_path
        if not destination_path.endswith("/"):
            destination_path += "/"

        # check if the path exists, if not, create it
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # Copy the class file to the new destination
        shutil.copyfile(xml_file, destination_path + current_file)


def extract_archive(archive_file):
    print("[+] Processing " + archive_file)
    temp_dir = tempfile.mkdtemp(prefix="jarjarbigs")

    archive = zipfile.ZipFile(archive_file, 'r')
    try:
        archive.extractall(temp_dir)
    except FileExistsError as file_exists_error:
        print(
            "[?] Warning! The archive \"{archive_file}\" seems to have a broken file structure. Found douplicate file when trying to write to \"{error_filepath}\". Continuing anyway, result most likely incomplete (please check the contents of the affected archive).".format(
                archive_file=archive_file, error_filepath=str(file_exists_error.filename)))
    except OSError as e:
        if e.errno == 36: # filename too long
            # restart extraction, this time perform a more manual extract and truncate long names
            bufsiz = 16 * 1024 # or more to speed things up
            with archive as zf:
                for info in zf.infolist():
                    outpath_rel = os.path.normpath(info.filename)
                    outpath_rel_truncated = truncate_path_if_exceeds_name_limit(info.filename)
                    if outpath_rel_truncated != outpath_rel:
                        print(f"[?] Warning! Encountered a file/directory path that contains names longer than the system name limit ({MAX_PATH_NAME_LEN} chars). Any parts longer than that will be truncated. \n        Found: {outpath_rel} \n    Truncated: {outpath_rel_truncated}")

                    outpath = temp_dir + os.sep + outpath_rel_truncated

                    if info.is_dir():
                        Path(outpath).mkdir(parents=True, exist_ok=True)
                    else:
                        with zf.open(info) as fin, open(outpath, 'wb') as fout:
                            while True:
                                buf = fin.read(bufsiz)
                                if not buf:
                                    break
                                fout.write(buf)
        else:
            raise  # re-raise previously caught exception

    directories = [temp_dir]

    dir_archives = scan_directory_shallow(temp_dir)
    if len(dir_archives) != 0:

        print("[+] new archive(s) found: " + str(dir_archives))

        for new_archive in dir_archives:
            if os.path.isfile(new_archive):
                tmp_dirs = extract_archive(new_archive)
                directories += tmp_dirs
            else:
                print("[?] Discovered folder which has a .jar \"extension\": " + str(new_archive))

    return directories


def create_jar_archive(source_directory, archive_name):
    print("[+] Creating jar archive " + archive_name)
    shutil.make_archive(archive_name, 'zip', source_directory)
    os.rename(archive_name + ".zip", archive_name)


def create_zip_archive(source_directory, archive_name):
    print("[+] Creating zip archive " + archive_name)
    shutil.make_archive(archive_name, 'zip', source_directory)
    os.rename(archive_name + ".zip", archive_name)


if __name__ == '__main__':
    print("--- jarjarbigs.py 0.1 by MOGWAI LABS GmbH --------------------------------------\n")

    parser = argparse.ArgumentParser(
        description="jarjarbigs.py - create a huge jar file from existing jar/war/ear files")
    parser.add_argument('source', help="source directory with jar/war/ear files")
    parser.add_argument('destination', help="destination jar file")
    parser.add_argument('-l', '--logfile', nargs=1, default=None,
                        help='Create a log file which jar contains which classes')
    parser.add_argument('-x', '--xml', nargs=1, default=None,
                        help='Create a second zip archive that contains all xml- and property files')

    arguments = parser.parse_args()

    if sys.version_info[0] < 3:
        print("[-] Please use Python3 (for zip64 support)")
        exit(2)

    if not os.path.isdir(arguments.source):
        print("[-] source does not exists or is not a directory")
        exit(1)

    archives = scan_directory_shallow(arguments.source)
    destination_directory = tempfile.mkdtemp(prefix="jarjarbigs")
    xml_destination_directory = tempfile.mkdtemp(prefix="jarjarbigs")

    for archive in archives:
        directories = extract_archive(archive)

        for source_directory in directories:
            copy_class_files(archive, source_directory, destination_directory)

            if arguments.xml is not None:
                copy_xml_files(archive, source_directory, xml_destination_directory)

            shutil.rmtree(source_directory)

    create_jar_archive(destination_directory, arguments.destination)

    if arguments.xml is not None:
        create_zip_archive(xml_destination_directory, arguments.xml[0])
    shutil.rmtree(destination_directory)
    shutil.rmtree(xml_destination_directory)
