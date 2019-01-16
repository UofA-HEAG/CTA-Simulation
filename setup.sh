#!/bin/bash
# First time setup script

# Change the CTA_PATH to wherever your own CTA installation is located
export CTA_PATH=$HOME/cta/CTA_MC

# Verify this is the location of your own /fast partition allocation
export FAST_PARTITION=/fast/users/`whoami`

# -------------------------------------------------------------------

# Get current directory this script is located in, from:
# https://stackoverflow.com/questions/59895/
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
export REPO_PATH="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"

# Call setup scripts located in different directories
for dir in data scripts; do
  echo "Running $dir setup..."
  ${REPO_PATH}/${dir}/setup.sh
done
