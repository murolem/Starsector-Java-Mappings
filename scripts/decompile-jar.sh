#!/bin/bash
set -e

printf "Script: Decompiles specified JAR.\n"
echo

SCRIPT_DIRPATH="$(realpath $0)"
SCRIPT_DIRPATH="$(dirname $SCRIPT_DIRPATH)"

JAVA_PATH="$SCRIPT_DIRPATH/../java"
DECOMPILER="$SCRIPT_DIRPATH/../decompiler.jar"

# check variables
if [ ! -f "$JAVA_PATH" ]; then
  echo "Java executable not found at '$JAVA_PATH'."
  exit 1
elif [ ! -f "$DECOMPILER" ]; then
  echo "Decompiler not found at '$DECOMPILER'."
  exit 1
fi

# check args
if [ $# -ne 2 ];
  then
    printf "ERROR: Expected 2 arguments, received %s. Provide exactly 2 arguments: \n(1) path to a JAR to decompile, \n(2) path to the directory to decompile to (will be created if missing).." $#
    echo
    exit 1
fi

JAR_PATH=$1
OUT_DIRPATH=$2

# validate args
if [ ! -f "$JAR_PATH" ]; then
  printf "ERROR: JAR not found at %s" "$JAR_PATH"
  echo
  exit 1
fi

if [ -d "$OUT_DIRPATH" ]; then
  printf "Output directory already exists. Continue by purging it? \nDirectory path: %s" "$OUT_DIRPATH"
  echo
  read -p "Confirm? (y/n) " -n 1 -r
  echo    # (optional) move to a new line
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
  fi

  printf "Removing %s" "$OUT_DIRPATH"
  echo
  rm -rf "$OUT_DIRPATH"
fi

# run command
"$JAVA_PATH" \
    -jar "$DECOMPILER" \
    "$JAR_PATH" \
    "$OUT_DIRPATH"