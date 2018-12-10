#!/bin/bash
# Setup all non-standard files for CTA CORSIKA/sim_telarray

CTA_PATH=${HOME}/cta/CTA_MC

# Get current directory this script is located in, from:
# https://stackoverflow.com/questions/59895/
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
WORK_PATH="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"

# Link files
ln -sf ${WORK_PATH}/INPUTS_CTA_PROD4-Paranal-5-SST-template-20deg ${CTA_PATH}/corsika-run
ln -sf ${WORK_PATH}/INPUTS_CTA_PROD4-Paranal-5-SST-template-20deg-flat-spectrum ${CTA_PATH}/corsika-run
