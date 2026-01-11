#!/bin/bash
set -e

printf "Script: Merges JARs in specified directory to a single JAR. Also applies additional processing - specifically, trimming long filenames.\n"
echo

SCRIPT_DIRPATH="$(realpath $0)"
SCRIPT_DIRPATH="$(dirname $SCRIPT_DIRPATH)"

PYTHON_COMMAND="python3"
JARJARBIGS_PY_SCRIPT_PATH="$SCRIPT_DIRPATH/python/jarjarbigs.py"

# check variables
if ! command -v "$PYTHON_COMMAND" >/dev/null 2>&1
then
    echo "ERROR: $PYTHON_COMMAND could not be found"
    exit 1
fi

# check args
if [ $# -ne 2 ]; 
  then
    printf "ERROR: Expected 2 arguments, received %s. Provide exactly 2 arguments: \n(1) source directory containing JARs and \n(2) output directory for the project.\n" $#
    exit 1
fi

JARS_DIRPATH=$1
OUTPUT_JAR_PATH=$2

# validate args
if [ ! -d "$JARS_DIRPATH" ]; then
  echo "ERROR: JARs dirpath '$JARS_DIRPATH' does not exist."
  exit 1
fi

# run command
$PYTHON_COMMAND \
    "$JARJARBIGS_PY_SCRIPT_PATH" \
    "$JARS_DIRPATH" \
    "$OUTPUT_JAR_PATH"