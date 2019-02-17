#!/bin/bash

# Move Data/ folder to /fast partition and symbolically link back
if [ ! -d ${FAST_PARTITION}/Data ]; then
  echo "Moving Data/ folder to /fast partition and linking..."
  mv ${CTA_PATH}/Data ${FAST_PARTITION}/
  ln -s ${FAST_PARTITION}/Data ${CTA_PATH}
fi

ask() {
  # Prompt users to do something
  if [ "${2:-}" = "Y" ]; then
    prompt="Y/n"
    default=Y
  elif [ "${2:-}" = "N" ]; then
    prompt="y/N"
    default=N
  else
    prompt="y/n"
    default=
  fi

  while true; do
    # Prompt question
    read -p "$1 [$prompt] " reply

    # Set default if no reply
    if [ -z $reply ]; then
        reply=$default
    fi

    # Check if the reply is valid
    case "$reply" in
      Y*|y*) return 0 ;;
      N*|n*) return 1 ;;
    esac
  done
}

# Ask if users want to have links to .job files in their /fast partition
# This is just a quality-of-life option so calls to sbatch in /fast don't need to specify the full path to the .job file
if ask "Would you like to create .job file symlinks in ${FAST_PARTITION}?" N; then
  for job in $( ls ${REPO_PATH}/scripts/batch/*.job ); do
    ln -sf $( readlink -f $job ) ${FAST_PARTITION}/$( basename $job )
  done
fi

get_cpus="scripts/get-cpus"

if [ ! -d ${HOME}/.local/bin ]; then
  >&2 echo "You do not have a ~/.local/bin directory. Some scripts are not able to be installed correctly. Please make this directory and run the setup again."
else
  ask "Install symlink for $get_cpus?" Y && ln -sf $( readlink -f $get_cpus ) ${HOME}/.local/bin/$( basename $get_cpus )
fi
