# Script Usage

This directory contains scripts used to manage CORSIKA and `sim_telarray` runs and job submission through the SLURM scheduler. As a note, none of the CORSIKA/`sim_telarray` scripts should be run by the user: they are instead called as part of a job submission script. The submission scripts are located in the `batch/` directory, each with a `.job` extension.

## SLURM Job Submission

Jobs may be submitted through the `sbatch` command. Note that output files from SLURM will be written in the directory that `sbatch` is called from. Therefore, it is a good idea to do this in the `/fast` partition so that these files do not take up space in the `/home` partition.

### Pre-Submission Checklist

Before job submission through SLURM, make sure you have

* Checked the script the `.job` file calls on the last line exists (and is correct)
* Changed to a directory in the `/fast` partition to prevent output files clogging up space in the `/home` partition
* Added all necessary run information to `production/runs.yml`, including a non-ambiguous human-readable summary. See [Adding a new run](../production/README.md#adding-a-run-to-runsyml) for more information on how to do this
* Specified the correct job name in the `.job` script (the `-J` option)

To make life easier, when submitting a job with an edited `.job` script, push both the `.job` script and the updated `production/runs.yml` file in the same commit. This makes it absolutely clear that the `.job` script in the repository at that time was the one used to submit the job added to `production/runs.yml`. See commits like [2e3e0fc](https://github.com/UofA-HEAG/CTA-Simulation/commit/2e3e0fc1e8ca582e8139e8e92d0e8b947f9ac2ea) and [1cbcd14](https://github.com/UofA-HEAG/CTA-Simulation/commit/1cbcd1496e1cc5bd2dc25018a6d10c8e263bd142) for examples on how this looks.

### Post-Submission Checklist

After submission and beyond, make sure to do the following:

* Check on the job to see when it has finished. See [Email Notification](#email-notification) to see how to get email alerts when this happens
* Add start and end times to the run's `job` section when appropriate. These times are found using the `rcstat <SLURM job id>` command
  * Make sure to add the current timezone (replacing the `T` with a space and adding _e.g._ `+10:30` to the end), as this is important when considering daylight savings
* Update the run's `status` as needed

### Email Notification

If you want to be notified by email when a job is finished, add the following to the `.job` script, after the other `#SBATCH` directives:

```sh
#SBATCH --mail-user=your.email@example.com
#SBATCH --mail-type=ALL
```

If you are unsure on what other `#SBATCH` directives do, or are interested in what other parameters may be used, consult the man page for `sbatch` through `man sbatch`.
