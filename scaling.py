#!/usr/bin/env python

import argparse
from datetime import timedelta
import os
import subprocess

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
parser.add_argument('--serial_time', dest="t1", type=float, default=0,
                    help='time limit in seconds for a serial run (default: no limit)')
parser.add_argument('--min_time', dest="t_min", type=float, default=0,
                    help='lower threshold in seconds for any run (default: no limit)')
parser.add_argument('--parallel_efficiency', type=float, default=0.9,
                    help='assumed parallel efficiency (default: 90 %)')

args = parser.parse_args()

for n in range(args.log2nodes + 1):
    ntasks = 2**n

    if args.scaling == "weak":
        ny = ny * ntasks

    jobname = f"{args.scaling}-{args.script}-{args.nx}-{args.nx}-{ntasks}"
    
    if args.t1 != 0:
        if args.scaling == "weak":
            tN = args.t1 * ntasks / args.parallel_efficiency
        else:
            tN = args.t1 / (args.parallel_efficiency * ntasks)
        
        tN = max(tN, args.t_min)
            
        # format run time for sbatch as d-h:mm:ss
        time_str = f"--time={str(timedelta(seconds=tN)).replace(' day, ', '-')}"
    else:
        time_str = ""    
    

    s = (
        f"sbatch --partition={args.partition} --exclusive --job-name={jobname} "
        f"--ntasks={ntasks} --ntasks-per-core=2 {time_str} "
        f"--output={os.getcwd()}/results/{args.partition}/{jobname}.slurmout "
        f"jobscript {args.script} {args.nx} {args.ny}"
    )
  
    print(s)
    subprocess.run(s, shell=True)
