# CTA MC Installation Guide

To install the CTA MC pipeline / CORSIKA & sim_telarray setup on Phoenix, you'll need a few things:

* `corsika_simtelarray.tar`: the CTA MC source code
* `qgsdat-II-03.dms`: QGS model 2 data
* `zstd`: file compressor

I'm assuming you've already got the first two downloaded in your home directory. The third we'll make ourselves because Phoenix doesn't have it as a module.

## `module` check

You'll only need this module to complete the installation:

```
GCCcore/6.3.0
```

Any other modules that give you GCC might be a bit risky to use, so make sure this is the only one. You can get this using the regular `module load GCCcore/6.3.0` command.

## `zstd` dependency

* Run these:

```bash
git clone https://github.com/facebook/zstd.git
cd zstd
make
make check
ln -s ~/zstd/programs/zstd ~/.local/bin
```

* Now the command `zstd` should be able to be run from anywhere.
* If not, you'll need to add `~/.local/bin` to your path. This can be done by adding the following line into your `~/.bashrc` and then sourcing it, or reopening the connection:

```bash
export $PATH="~/.local/bin:${PATH}"
```

## CTA MC

* Run these commands

```bash
mkdir CTA_MC
cd CTA_MC
tar -xvf ../corsika_simtelarray.tar
cp ../qgsdat-II-03.dms qgsdat-II-03
./build_all prod4-paranal-baseline qgs2
```

If you get your bash prompt back, type `exit` to return back to the build. For whatever reason, the build might stop here just as it's about to execute a csh script. I would also be afraid if I were about to execute a csh script, so I can understand why bash might be a bit apprehensive about it.

The final bit printed out from ths build process should be `Everything built and ready to run the examples.`. You can ignore the `cp` and `/bin/ls` errors as they aren't relevant to the Prod4 work.

* Next, you need to edit the `examples_common.sh` file. Comment out lines 6 and 7 and change line 39 to `export LD_LIBRARY_PATH="${HESSIO_PATH}/lib:${LD_LIBRARY_PATH}"`. This stops `examples_common.sh` from incorrectly assuming the program works when the computer doesn't know where any shared libraries the program needs are.
* Now, you should be ready to run CORSIKA and sim_telarray!

As an example, you could do this and things shouldn't complain or not work for you:

```bash
export NSHOW=1
./example_scripts/Prod4/prod4_sst-only_run
./example_scripts/Prod4/prod4_sst-only_sim5 1
```
