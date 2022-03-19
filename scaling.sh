#!/bin/sh

#SBATCH --array=0-6%1
#SBATCH --time=12:00

scaling=$1
script=$2
nx=$3
ny=$4

ntasks=$((2 ** SLURM_ARRAY_TASK_ID))
if  [ $scaling == "weak" ]; then
    ny=$((ny * ntasks))
fi

jobname=$scaling-$nx-$ny-$ntasks

sbatch --partition=$SBATCH_PARTITION --job-name=$jobname --ntasks=$ntasks --ntasks-per-core=2 \
  --output=${PWD}/results/$SBATCH_PARTITION/$jobname.slurmout \
  jobscript $script $nx $ny
