#!/bin/bash

partition=$1
scaling=$2
script=$3
nx=$4
ny=$5

for n in {0..6}; do
    ntasks=$((2 ** n));

    if  [ $scaling == "weak" ]; then
        ny=$((ny * ntasks))
    fi

    jobname=$scaling-$nx-$ny-$ntasks

    sbatch --partition=$partition --exclusive --job-name=$jobname \
      --ntasks=$ntasks --ntasks-per-core=2 \
      --output=${PWD}/results/$partition/$jobname.slurmout \
      jobscript $script $nx $ny
done
