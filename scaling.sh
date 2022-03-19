#!/bin/sh

#SBATCH --time=12:00

queue=fast

for n in {0..6}; do
    size=$((2 ** n));
    id=`sbatch --partition=$queue --job-name=$size-strong --ntasks=$size --ntasks-per-core=2 --output=${PWD}/results/$queue/strong-$size.slurmout jobscript`
    echo "ntasks $n jobid $id size $size"
done
