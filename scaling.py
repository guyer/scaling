#!/usr/bin/env python

import argparse
import os
import subprocess

from slurmutils.slurmtime import slurm2delta, delta2slurm, round_seconds, zero

parser = argparse.ArgumentParser(description='Drive a set of scaling runs')
parser.add_argument('script', type=str,
                    help='FiPy script to perform scaling study on')
parser.add_argument('--partition', dest='partition', type=str, required=True,
                    help='Request a specific partition for the resource allocation.')
parser.add_argument('--strong', dest='scaling', action='store_const',
                    const="strong", default="strong",
                    help='Perform strong scaling (fixed problem size) (default: "strong"')
parser.add_argument('--weak', dest='scaling', action='store_const',
                    const="weak", default="strong",
                    help='Perform weak scaling (variable problem size) (default: "strong"')
parser.add_argument('--nx', type=int, default=100,
                    help='number of cells in x direction (default: 100)')
parser.add_argument('--ny', type=int, default=100,
                    help='number of cells in y direction (default: 100)')
parser.add_argument('--log2nodes', type=int, default=6,
                    help='maximum power of 2 for number of tasks (default: 6)')
parser.add_argument('--serial-time', dest="t1", type=str, default="0",
                    help='''Total run time of a serial job allocation (default: "0").

                    In concert with `--min-time`, `--parallel-efficiency`,
                    the type of scaling, and the number of tasks, sets a
                    limit on the total run time of each job allocation.

                    A time limit of zero requests that no time limit be
                    imposed.  Acceptable time formats include "minutes",
                    "minutes:seconds", "hours:minutes:seconds",
                    "days-hours", "days-hours:minutes" and
                    "days-hours:minutes:seconds".
                    ''')
parser.add_argument('--min-time', dest="t_min", type=str, default="0",
                    help='''lower time threshold for any run (default: "0")

                    See `--serial-time` for allowed time formats.
                    ''')
parser.add_argument('--parallel-efficiency', type=float, default=0.9,
                    help='assumed parallel efficiency (default: 90 %)')
parser.add_argument('--conda-path', type=str, default="/working/guyer/mambaforge/bin/conda",
                    help='''Path to conda installation (default: "/working/guyer/mambaforge/bin/conda").

                    Per emails with reida and tnk10 on 2022-03-18:
                    invoke conda in /tmp because of configuration/malefactor-induced
                    performance issues on /working.
                    ''')
parser.add_argument('--conda-env', type=str, default="fipy3k",
                    help='Conda environment to run in (default: "fipy3k")')

args = parser.parse_args()

t1 = slurm2delta(args.t1)
t_min = slurm2delta(args.t_min)

for n in range(args.log2nodes + 1):
    ntasks = 2**n

    if args.scaling == "weak":
        ny = ny * ntasks

    jobname = "{}-{}-{}-{}-{}".format(args.scaling, args.script, args.nx, args.nx, ntasks)
    
    if t1 == zero:
        time_option = []
    else:
        # calculate approximate job time based
        # on serial time and scaling assumption
        p = args.parallel_efficiency
        if args.scaling == "weak":
            tN = t1 * ntasks / (1 - p + p * ntasks)
        else:
            tN = t1 * (1 - p + p / ntasks)
        
        tN = round_seconds(max(tN, t_min))
            
        # format run time for sbatch as d-h:mm:ss
        time_option = ['--time={}'.format(delta2slurm(tN))]
    

    run_args = (
        [
            "sbatch", "--partition={}".format(args.partition), "--exclusive",
            "--job-name={}".format(jobname),
            "--ntasks={}".format(ntasks), "--ntasks-per-core=2",
            "--output={}/results/{}/{}.slurmout".format(os.getcwd(),
                                                        args.partition, jobname)
        ]
        + time_option
        + [
            "jobscript", args.script, str(args.nx), str(args.ny),
            args.conda_path, args.conda_env
        ]
    )

    print(" ".join(run_args))
    subprocess.run(run_args)
