# Script Usage

This directory contains scripts used to manage CORSIKA and `sim_telarray` runs and job submission through the SLURM scheduler. As a note, none of the CORSIKA/`sim_telarray` scripts should be run by the user: they are instead called as part of a job submission script. The submission scripts are located in the `batch/` directory, each with a `.job` extension.

## SLURM Job Submission

Jobs may be submitted through the `sbatch` command. Note that output files from SLURM will be written in the directory that `sbatch` is called from. Therefore, it is a good idea to do this in the `/fast` partition so that these files do not take up space in the `/home` partition.

### Pre-Submission Checklist

Before job submission through SLURM, make sure you have

* Checked the script the `.job` file calls on the last line exists
* Changed to a directory in the `/fast` partition to prevent output files clogging up space in the /home partition
* Added all necessary run information to `production/runs.yml`, including a non-ambiguous human-readable summary
* Specified the correct job name in the `.job` script (the `-J` option)

### Email Notification

If you want to be notified by email when a job is finished, add the following to the `.job` script, after the other `#SBATCH` directives:

```sh
#SBATCH --mail-user=your.email@example.com
#SBATCH --mail-type=ALL
```

If you are unsure on what other `#SBATCH` directives do, or are interested in what other parameters may be used, consult the man page for `sbatch` through `man sbatch`.
