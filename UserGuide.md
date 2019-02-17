# User Guide

This document serves as a brief introduction to the CTA simulation pipeline and the Phoenix supercomputer.

## Contents

* [The Simulation Pipeline](#the-simulation-pipeline)
  * [CORSIKA](#corsika)
  * [`sim_telarray`](#sim_telarray)
* [Phoenix](#phoenix)
  * [Modules](#modules)
  * [SLURM](#slurm)
    * [SLURM Programs](#slurm-programs)
    * [Array Jobs](#array-jobs)
    * [Updating Job Parameters](#updating-job-parameters)
  * [Monitoring Resources on Phoenix](#monitoring-resources-on-phoenix)
* [Bibliography](#bibliography)

## The Simulation Pipeline

Currently, the CTA collaboration uses simulations predominantly to evaluate the sensitivity of the telescope candidates.
The simulation is divided into two separate parts: the simulation of air showers in the upper atmosphere by gamma rays and cosmic rays, and the subsequent triggering and detection by pixels in each telescope of the air shower.
The resulting data is then used in further analyses which are not covered by the scope of this guide.

The air shower simulation is handled by CORSIKA, whilst the simulation of the telescope array is done by `sim_telarray`.
This chapter will present a surface overview of both programs, with any further technical questions referred to the respective user guides of both programs.

### CORSIKA

CORSIKA [[1](#bibliography)] is a program originally written for the KASKADE experiment in the late 90s.
It is primarily written in fixed format Fortran 77, and supports different particle interaction models which are used to simulate particle air showers through the Earth's atmosphere.
The model used for CTA simulations is the QGSJET-II model [[2](#bibliography)].
CORSIKA also supports various packages that extend the default behaviour.
As part of the CTA toolkit, CORSIKA uses the IACT/ATMO package [[3](#bibliography)] to gather emitted Cherenkov light from air shower events that are incident on an array of telescopes.

The Prod4 CTA toolkit uses CORSIKA v6.990, whose user guide should be included in some format alongside this guide.

### `sim_telarray`

`sim_telarray` [[4](#bibliography)] \(also known as `sim_hessarray`\) is a program written to simulate how telescopes receive and process the Cherenkov light received from air showers.
Primarily written in C, the program works with output from the IACT/ATMO CORSIKA package.

The Prod4 CTA toolkit uses `sim_telarray` v1541504878.

## Phoenix

This section covers topics like loading and unloading software modules, and handling SLURM on Phoenix.

### Modules

Phoenix allows users to choose different versions of software through Lmod.
This is invoked using the `module` command.
A list of some commonly-used commands is listed below:

* `module avail`: list all available modules
* `module list`: list the currently loaded modules
* `module load <module>`: load `<module>`
* `module unload <module>`: unload `<module>`
* `module purge`: unload all currently loaded modules
* `module help`: print out help information

### SLURM

SLURM is the scheduling software used on Phoenix to allocate computational resources to user-submitted jobs.
In general, when talking about jobs there are two main types:

* Interactive jobs: ones that give the user a terminal on the compute resources requested (be it CPU or GPU) to test and run code interactively
* Batch jobs: ones whose execution is defined in a script and are processed and run automatically by Phoenix

More specific to SLURM is the concept of an array job, which is a subset of batch jobs that run the same computation in parallel.
These jobs will be discussed later.

#### SLURM Programs

SLURM exposes a selection of different programs accessible from the command line that are used to submit, query and cancel jobs, namely:

* `sbatch`: submit batch jobs
* `scancel`: cancel currently running programs
* `squeue`: examine the current job queue
* `srun`: submit interactive jobs
* `sacct`: examine in-depth information of jobs
* `sstat`: examine in-depth information of currently running jobs
* `scontrol`: show resource usage, update job parameters

As with nearly all programs on the command line, usage information of these, including a full description of the available command line options, is provided in the manual pages through `man <command>`.

The programs that will be used most often in submitting and managing jobs are `sbatch`, `scancel` and `squeue`.

#### Array Jobs

As previously discussed, array jobs differ from regular SLURM jobs as they spawn a set of jobs, each running the same submission script.
They are created by the inclusion of the `array` parameter at submission time.
As each array task has a different task ID accessible through the `SLURM_ARRAY_TASK_ID` environment variable, this can be used to slightly tweak input parameters, say to split a large energy range into smaller chunks, each processed by a different array task.

See the `--array` entry in `man sbatch` for more information on the syntax of.

#### Updating Job Parameters

Job parameters can only be updated for jobs that have not begun running.
This is particularly useful for array jobs, which can have some jobs still waiting to run.
In such a case, parameters such as walltime and CPU memory of the remaining jobs can be updated in response to how eariler jobs fair.
For example, if it is seen that a job with ID `12345678` has array tasks that are failing as they hit the requested memory limit, the remaining jobs can be updated through `scontrol`.
Changing the memory requirements to 4 GB is done using:

```sh
scontrol update JobId=12345678 MinMemoryCPU=4096
```

Note that the `MinMemoryCPU` parameter takes memory size in MB.
Other parmeters that might be useful to change are:

* Walltime: `TimeLimit`
* Compute partition/queue: `Partition`

Again, see `man scontrol` for more details.
Note that `scontrol` only works for jobs that are currently in the queue, and that some parameters require administrator privileges to update.
Printing out information from jobs that have finished should be done through `sacct`.

### Monitoring Resources on Phoenix

When submitting jobs to Phoenix, it may be useful to know how many resources are available, _i.e._ when attempting to diagnose why some jobs aren't running.
Although some information about job status is accessible through `squeue`, the `scontrol` command reports on the amount of cores available at any given time, among other things.
However, its output is not necessarily user-friendly and so a purpose-built Python script has been written to aggregate this information and present it in a clearer format, found in `scripts/get-cpus`.
By default, this script computes the maximum number of tasks freely available for a program that requires 4 OMP threads per task.
This can be ignored, with the more important information contained within the `free cpus` column.
This reports the number of CPUs that are either on an idle, unused node (`idle`), or part of a node with both free and used cores (`mixed`).

## Bibliography

[1] D. Heck et al. _CORSIKA: A Monte Carlo code to simulate extensive air showers._ Tech. rep. FZKA-6019; LK 01; Wissenshaftliche Berchte. Karlsruher Institut Für Technologie, 1998-02.

[2] S. Ostapchenko. "QGSGET-II: Towards reliable description of very high energy hadronic interactions." In: _Nucl. Phys. Proc. Suppl._ 151 (2006), pp. 143-146. DOI: [10.1016/j.nuclphysbps.2005.07.026](http://dx.doi.org/10.1016/j.nuclphysbps.2005.07.026). arXiv: [hep-ph/0412332 [hep-ph]](https://arxiv.org/abs/hep-ph/0412332).

[3] K. Bernlöhr. _The IACT/ATMO package for CORSIKA_. 2017-10. URL: [https://www.mpi-hd.mpg.de/hfm/bernlohr/iact-atmo/](https://www.mpi-hd.mpg.de/hfm/bernlohr/iact-atmo/).

[4] K. Bernlöhr. _The sim\_telarray program for simulating atomspheric Cherenkov telescopes_. 2018-08. URL: [https://www.mpi-hd.mpg.de/hfm/bernlohr/sim_telarray/](https://www.mpi-hd.mpg.de/hfm/bernlohr/sim_telarray/).
