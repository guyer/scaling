#!/bin/sh

#SBATCH --array=0-6%1
#SBATCH --time=12:00

queue=fast

ntasks=$((2 ** SLURM_ARRAY_TASK_ID))

sbatch --partition=$SBATCH_PARTITION --job-name=$ntasks-strong --ntasks=$ntasks --ntasks-per-core=2 \
  --output=${PWD}/results/$SBATCH_PARTITION/strong-$nsize.slurmout \
  jobscript
