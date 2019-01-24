#!/usr/bin/python -E
# This script reports usage as well as efficiency of requested parameters
# Usage includes elapsed walltime, CPU memory

# Giving this script a job ID, I just want a file with:
# job_id_taskno elapsed_time requested_time

from argparse import ArgumentParser
from collections import namedtuple
from getpass import getuser
from glob import glob
from itertools import starmap
from os import path
import re
import subprocess

SUFFIXES = {
    'K': 10,
    'M': 20,
    'G': 30,
    'T': 40,
    'P': 50,
    'E': 60
}

CORSIKA = 'corsika'
SIMTEL = 'simtel'


def proc_to_seconds(val, entry):
    """Converts minutes to seconds"""
    return 60 * int(val)


def proc_to_int(val, entry):
    """Converts a value to integer"""
    return int(val)


def proc_reqmem_to_bytes(val, entry):
    """Returns size in bytes and flag for a per node or per CPU quantity"""
    size_val, per_flag = val[:-1], val[-1]
    return proc_to_bytes(size_val, entry), per_flag


def proc_to_bytes(val, entry):
    """Converts a value in the form [0-9]+(K|M|G|T|P|E) to bytes

    This method also uses the entry tuple to check if this quantity is defined
    as per node or per CPU by checking the end flag of the ReqMem field. It
    then scales the resulting bytes by the number of allocated CPUs per node
    if the quantity should be defined as per CPU.
    """
    if val is None or val == '16?':
        return 0.0

    # Check if the ReqMem quantity (and thus all others) is per node or per CPU
    if entry.ReqMem.endswith('n'):
        factor = 1.0
    elif entry.ReqMem.endswith('c'):
        factor = float(entry.AllocCPUS) / float(entry.AllocNodes)
    else:
        raise ValueError('Unknown ReqMem suffix {!r}'.format(entry.ReqMem[-1]))

    size, suffix = val[:-1], val[-1]

    # Check for when bytes have already been given (no suffix)
    if suffix not in SUFFIXES:
        return float(val) * factor

    scale = 2 ** SUFFIXES.get(suffix)
    return scale * float(size) * factor


SacctField = namedtuple('SacctField', 'name process')
FIELDS = [
    # number of allocated CPUs
    SacctField('AllocCPUS', proc_to_int),
    # number of allocated nodes
    SacctField('AllocNodes', proc_to_int),
    # elapsed time (in seconds)
    SacctField('ElapsedRaw', proc_to_int),
    # requested time limit (in minutes)
    SacctField('TimelimitRaw', proc_to_seconds),
    # max resident set size of all tasks in job in KB
    SacctField('MaxRSS', proc_to_bytes),
    # minimum required memory for the job in MB
    SacctField('ReqMem', proc_reqmem_to_bytes),
    # max number of page faults of all tasks in job
    SacctField('MaxPages', proc_to_bytes),
    # max virtual memory size of all tasks in job
    SacctField('MaxVMSize', proc_to_bytes),
]
FIELD_FMT_STR = 'JobID,' + ','.join(f.name for f in FIELDS)

# A SacctEntry does not have a JobID field, the task number is stored as keys
# in a dictionary instead
SacctEntry = namedtuple('SacctEntry', [f.name for f in FIELDS])
OutEntry = namedtuple(
    'OutEntry',
    [f.name for f in FIELDS] + ['OutputFileSize']
)

OUTPUT_HEADER = [
    'TaskNo',
    'ElapsedTime',
    'RequestedTime',
    'MaxMemUsage',
    'ReqestedMem',
    'OutputFileSize',
    'MaxVirtualMemUsage',
    'MaxPageFaults',
    'PerFlag'
]


def get_task_no(job_id):
    """Extract the task number from the full job/job step ID"""
    task_info = job_id.split('_')[1]
    task_no = task_info.split('.')[0] if '.batch' in task_info else task_info
    return int(task_no)


def get_sacct_stats(job_id):
    """Return a tuple of task_no, task_no values from sacct"""
    result = subprocess.Popen(['sacct', '--parsable', '--noheader',
                               '--format={}'.format(FIELD_FMT_STR),
                               '-j', job_id],
                              stdout=subprocess.PIPE)

    for line in result.stdout:
        values = line.strip().split('|')[:-1]
        clean_values = [v if v else None for v in values]
        yield get_task_no(clean_values[0]), clean_values[1:]


def get_corsika_slurm_map(job_id, slurm_out_dir):
    """Return a dict of SLURM task number to CORSIKA run number"""
    regexp = r'Real working directory is ([\w\/]+)'
    slurm_files = path.join(slurm_out_dir, 'slurm-{}_*.out'.format(job_id))
    result = subprocess.Popen(['grep', '-Poe', regexp] + glob(slurm_files),
                              stdout=subprocess.PIPE)

    def filename(x):
        """Return basename with file extension stripped"""
        return path.splitext(path.basename(x))[0]

    res = {}

    for line in result.stdout:
        # Separate grep output into SLURM output and grep regexp match
        slurm_out_path, match = line.split(':')

        corsika_path = re.match(regexp, match).group(1)
        task_no = get_task_no(filename(slurm_out_path))
        run_no = int(filename(corsika_path)[3:])
        res[run_no] = task_no

    return res


def get_disk_usage(file_globs, r_min):
    """Retrieves disk usage for given list of file globs and writes to dict"""
    run_files = sum(map(glob, file_globs), [])

    result = subprocess.Popen(['du'] + run_files,
                              stdout=subprocess.PIPE)

    res = {}

    for run_no, line in enumerate(result.stdout, start=r_min):
        byte_size, file_path = line.strip().split()
        res[run_no] = (float(byte_size), )

    return res


def get_corsika_du(cta_path, r_min, r_max, **kwargs):
    """Get disk usage for a range of CORSIKA runs

    r_min and r_max are the minimum and maximum CORSIKA run numbers considered,
    inclusive.
    """
    if r_max < r_min:
        raise ValueError('Maximum CORSIKA run smaller than minimum '
                         '({} < {})'.format(r_max, r_min))

    # Generate globs for CORSIKA output files
    run_stubs = ['{:06}'.format(i) for i in xrange(r_min, r_max + 1)]
    run_globs = [path.join(cta_path,
                           'Data/corsika/run{}/run*.zst'.format(run_no))
                 for run_no in run_stubs]

    return get_disk_usage(run_globs, r_min)


def get_simtel_du(cta_path, r_min, r_max, sst_type='astri+chec-s'):
    """Get disk usage for a range of sim_telarray runs

    r_min and r_max are the minimum and maximum sim_telarray numbers
    considered, inclusive. They are equivalent to the CORSIKA run numbers, and
    so are referred to as such.

    sst_type is the type of SST used in the simulation. This shouldn't need to
    change, but is left as a variable in case it needs to.
    """
    if r_max < r_min:
        raise ValueError('Maximum CORSIKA run smaller than minimum '
                         '({} < {})'.format(r_max, r_min))

    sim_tel_root = path.join(cta_path, 'Data/sim_telarray',
                             'cta-prod4-sst-{}'.format(sst_type),
                             '0.0deg/Data')
    run_globs = [path.join(sim_tel_root, '*_run{}_*.simtel.zst'.format(i))
                 for i in xrange(r_min, r_max + 1)]

    return get_disk_usage(run_globs, r_min)


GET_DU = {
    CORSIKA: get_corsika_du,
    SIMTEL: get_simtel_du,
}


def get_stats(job_id, job_type, mapping, cta_path):
    """Return usage stats from a given job ID and job type"""
    min_run_no, max_run_no = min(mapping), max(mapping)

    print('Retrieving stats from SLURM job {}...'.format(job_id))
    du = GET_DU[job_type](cta_path, min_run_no, max_run_no)
    entries = get_sacct_stats(job_id)

    tasks = {}

    # Consolidate duplicate entries with merge_rows
    for task_no, e in entries:
        if task_no not in tasks:
            tasks[task_no] = e
        else:
            tasks[task_no] = merge_rows(tasks[task_no], e)

    # Process each entry into a usable form
    for task_no, e in tasks.iteritems():
        tasks[task_no] = process_entry(e)

    # For CORSIKA, only need to map `du` to SLURM task numbers as `tasks`
    # already has the correct keys
    if job_type == CORSIKA:
        tasks = cat_dict_tuples(tasks, map_to_slurm(du, mapping))

    # For simtel, both dicts are in terms of CORSIKA run number and so
    # must be mapped to SLURM task number after merging
    elif job_type == SIMTEL:
        tasks = map_to_slurm(cat_dict_tuples(tasks, du), mapping)

    else:
        raise ValueError('Invalid job_type {!r}'.format(job_type))

    # Sort entries and return
    return sorted(tasks.iteritems(), key=lambda x: x[0])


def merge_rows(row1, row2):
    """Merge duplicate rows

    In order for a subsequent call to process_entry() to work, this function
    must convert tuples into SacctEntry namedtuples such that processing can
    be done.
    """

    def keep_first_value(x, y):
        """Keeps first non-None argument - a value"""
        return y if x is None else x

    res = starmap(keep_first_value, zip(row1, row2))
    return SacctEntry(*res)


def process_entry(entry):
    """Process an unprocessed entry into a more consistent, usable form

    Note this method does not create a namedtuple. This is so that the
    processed sacct entries can be merged with information taken from
    other sources, such as du.
    """
    return tuple(f.process(entry[i], entry) for i, f in enumerate(FIELDS))


def map_to_slurm(corsika_dict, mapping):
    """Map a dictionary's CORSIKA run keys to SLURM task keys using mapping"""
    res = {}
    for run_no, content in corsika_dict.iteritems():
        res[mapping[run_no]] = content
    return res


def cat_dict_tuples(d1, d2):
    """Concatenate tuples across two dictionaries when keys match"""
    res = d1.copy()

    for k2, v2 in d2.iteritems():
        res[k2] = res[k2] + d2[k2]

    return res


def write_task_to_csv(file, task):
    """Write individual task record to a file in .csv format"""
    task_no, e = task
    entry = OutEntry(*e)

    output = [
        task_no,
        entry.ElapsedRaw,
        entry.TimelimitRaw,
        entry.MaxRSS,
        entry.ReqMem[0],
        entry.OutputFileSize,
        entry.MaxVMSize,
        entry.MaxPages,
        entry.ReqMem[1],
    ]

    file.write(','.join(map(str, output)) + '\n')


def write_stats(tasks, job_id, job_type):
    """Write a full set of tasks containing statistics to .csv format"""
    out_filename = '{}-{}.stat'.format(job_id, job_type)
    print('Writing stats to {!r}...'.format(out_filename))

    with open(out_filename, 'w') as f:
        f.write(','.join(OUTPUT_HEADER) + '\n')
        for task in tasks:
            write_task_to_csv(f, task)


def make_parser():
    """Make the command line argument parser"""
    parser = ArgumentParser(
        description='Extract usage stats from SLURM array jobs and write '
        'out to file.'
    )

    def job_id(x):
        """Determine if a job ID looks valid or not"""
        if set(x) - set('0123456789'):
            raise ValueError
        else:
            return x

    def directory(x):
        """Determine if a directory exists or not"""
        if not path.isdir(x):
            raise ValueError
        else:
            return x

    parser.add_argument(
        'corsika_job_id',
        metavar='CORSIKA_JOB_ID',
        type=job_id,
        help='a SLURM array job ID corresponding to a CORSIKA run '
        "without a task number, e.g. '193852'"
    )

    parser.add_argument(
        'simtel_job_id',
        metavar='SIMTEL_JOB_ID',
        type=job_id,
        nargs='?',
        help='a SLURM array job ID corresponding to a sim_telarray run'
    )

    parser.add_argument(
        '-c', '--cta-path',
        metavar='DIR',
        dest='cta_path',
        default='/home/{}/CTA_MC'.format(getuser()),
        type=directory,
        help='path to CTA files (default: %(default)s)'
    )

    parser.add_argument(
        '-o', '--slurm-output-dir',
        metavar='DIR',
        dest='slurm_out_dir',
        default='/fast/users/{}'.format(getuser()),
        type=directory,
        help='directory for SLURM output files (default: %(default)s)'
    )

    return parser


def main():
    args = make_parser().parse_args()

    mapping = get_corsika_slurm_map(args.corsika_job_id, args.slurm_out_dir)

    corsika_tasks = get_stats(args.corsika_job_id, CORSIKA,
                              mapping, args.cta_path)

    write_stats(corsika_tasks, args.corsika_job_id, CORSIKA)

    if args.simtel_job_id:
        simtel_tasks = get_stats(args.simtel_job_id, SIMTEL,
                                 mapping, args.cta_path)

        write_stats(simtel_tasks, args.simtel_job_id, SIMTEL)


if __name__ == '__main__':
    exit(main())
