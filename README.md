# CTA-Simulation

This repository collects information on how to run CTA simulations:
- Installation instructions for phoenix
- Scripts to run CORSIKA and sim_telarray

## First Time Setup

If this is your first time using the repo, there is a first-time setup you can run located in `setup.sh`. Before running, edit the file to change `CTA_PATH` to where the CTA root directory is that contains CORSIKA and `sim_telarray`. You may also verify that `FAST_PARTITION` points to where your own user folder is on the `/fast` partition.

This script prepares the default CTA toolkit to be run on Phoenix using the data and scripts located in this repository.
