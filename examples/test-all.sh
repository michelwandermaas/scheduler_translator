#!/bin/bash

for file in test-UGE*sh
do
  echo $file
  target=`echo $file | sed -e 's%UGE%SLURM%'`
  ../translate_script.py $file -i UGE -o SLURM | tee $target >/dev/null
done
