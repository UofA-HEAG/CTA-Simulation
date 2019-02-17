# CTA-Simulation

This repository is a central hub for the running, maintenance, and documentation of CTA simulation pipeline jobs on Phoenix.

* Installation instructions for Phoenix
* Scripts to run CORSIKA and `sim_telarray`
* A yaml database to store production run, build and job submission information

## First Time Setup

If this is your first time using the repo, there is a first time setup you can run located in `setup.sh`. Before running, edit the file to change `CTA_PATH` to where the CTA root directory is that contains CORSIKA and `sim_telarray`. You should also verify that `FAST_PARTITION` points to where your own user folder is on the `/fast` partition.

This script prepares the default CTA toolkit to be run on Phoenix using the data and scripts located in this repository.

## Contents

* [Installation](Installation.md)
* [User Guide](UserGuide.md)
* [Managing the yaml database](production/README.md)
* [Using submission scripts](scripts/README.md)
