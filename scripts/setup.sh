#!/bin/bash

# Move Data/ folder to /fast partition and symbolically link back
if [ ! -d ${FAST_PARTITION}/Data ]; then
  echo "Moving Data/ folder to /fast partition and linking..."
  mv ${CTA_PATH}/Data ${FAST_PARTITION}/
  ln -s ${FAST_PARTITION}/Data ${CTA_PATH}
fi
