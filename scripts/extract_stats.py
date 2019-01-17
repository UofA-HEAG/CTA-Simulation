#!/usr/bin/python -E
# This script reports usage as well as efficiency of requested parameters
# Usage includes elapsed walltime, CPU memory

# Giving this script a job ID, I just want a file with:
# job_id_taskno elapsed_time requested_time

from argparse import ArgumentParser
from collections import namedtuple
from itertools import starmap
import subprocess

SUFFIXES = {
    'K': 10,
    'M': 20,
    'G': 30,
    'T': 40,
    'P': 50,
    'E': 60
}


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


Field = namedtuple('Field', 'name process')
FIELDS = [
    # number of allocated CPUs
    Field('AllocCPUS', proc_to_int),
    # number of allocated nodes
    Field('AllocNodes', proc_to_int),
    # elapsed time (in seconds)
    Field('ElapsedRaw', proc_to_int),
    # requested time limit (in minutes)
    Field('TimelimitRaw', proc_to_seconds),
    # max resident set size of all tasks in job in KB
    Field('MaxRSS', proc_to_bytes),
    # minimum required memory for the job in MB
    Field('ReqMem', proc_reqmem_to_bytes),
    # max number of page faults of all tasks in job
    Field('MaxPages', proc_to_int),
    # max virtual memory size of all tasks in job
    Field('MaxVMSize', proc_to_bytes),
]
FIELD_FMT_STR = 'JobID,' + ','.join(f.name for f in FIELDS)

# An Entry does not have a JobID field
Entry = namedtuple('Entry', [f.name for f in FIELDS])

OUTPUT_HEADER = [
    'TaskNo',
    'ElapsedTime',
    'RequestedTime',
    'MaxMemUsage',
    'ReqestedMem',
    'MaxVirtualMemUsage',
    'MaxPageFaults',
    'PerFlag'
]


def get_task_no(job_id):
    """Extract the task number from the full job/job step ID"""
    task_info = job_id.split('_')[1]
    task_no = task_info.split('.')[0] if '.batch' in task_info else task_info
    return int(task_no)


def get_entries(job_id):
    """Return a tuple of task_no, task_no values from sacct"""
    result = subprocess.Popen(['sacct', '--parsable', '--noheader',
                               '--format={}'.format(FIELD_FMT_STR),
                               '-j', job_id],
                              stdout=subprocess.PIPE)

    for line in result.stdout:
        values = line.strip().split('|')[:-1]
        clean_values = [v if v else None for v in values]
        yield get_task_no(clean_values[0]), clean_values[1:]


def merge_rows(row1, row2):
    """Merge duplicate rows"""

    def keep_first_value(x, y):
        """Keeps first non-None argument - a value"""
        return y if x is None else x

    res = starmap(keep_first_value, zip(row1, row2))
    return Entry(*res)


def process_entry(entry):
    """Process an unprocessed entry into a more consistent, usable form"""
    res = [f.process(entry[i], entry) for i, f in enumerate(FIELDS)]
    return Entry(*res)


def write_task_to_file(file, task):
    task_no, e = task
    entry = Entry(*e)

    output = [
        task_no,
        entry.ElapsedRaw,
        entry.TimelimitRaw,
        entry.MaxRSS,
        entry.ReqMem[0],
        entry.MaxVMSize,
        entry.MaxPages,
        entry.ReqMem[1],
    ]

    file.write(','.join(map(str, output)) + '\n')


def make_parser():
    parser = ArgumentParser(description='%(prog)s, '
                            'extract values from SLURM array jobs and '
                            'write out to file.')

    def job_id(x):
        """Determine if a job ID looks valid or not"""
        if set(x) - set('0123456789'):
            raise ValueError
        else:
            return x

    parser.add_argument(
        'job_id',
        metavar='JOB_ID',
        type=job_id,
        help="a SLURM array job ID without a task number, e.g. '193852'"
    )

    return parser


def main():
    args = make_parser().parse_args()
    entries = get_entries(args.job_id)

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

    # Sort entries
    sorted_tasks = sorted(tasks.iteritems(), key=lambda x: x[0])

    # Write each task to file
    with open('{}.stat'.format(args.job_id), 'w') as f:
        f.write(','.join(OUTPUT_HEADER) + '\n')
        for task in sorted_tasks:
            write_task_to_file(f, task)


if __name__ == '__main__':
    exit(main())
