#!/bin/bash

# Move Data/ folder to /fast partition and symbolically link back
if [ ! -d ${FAST_PARTITION}/Data ]; then
  echo "Moving Data/ folder to /fast partition and linking..."
  mv ${CTA_PATH}/Data ${FAST_PARTITION}/
  ln -s ${FAST_PARTITION}/Data ${CTA_PATH}
fi

# Ask if users want to have links to .job files in their /fast partition
# This is just a quality-of-life option so calls to sbatch in /fast don't need to specify the full path to the .job file
while true; do
  read -p "Would you like to create .job file links in ${FAST_PARTITION}? [y/N] " reply

  if [ -z $reply ]; then
    reply=N
  fi

  case "$reply" in
    Y*|y*)
      for job in $( ls ${REPO_PATH}/scripts/batch/*.job ); do
        ln -sf $( readlink -f $job ) ${FAST_PARTITION}/$( basename $job )
      done
      ;;
    N*|n*)
      break ;;
  esac

  printf "Invalid reply '%s'\n" $reply
done
