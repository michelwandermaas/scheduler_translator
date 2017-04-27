#!/bin/bash
#
# == Set SGE options:
#
## run the job in the current working directory (where qsub is called)
#$ -cwd
## submit the job to the high priority queue
#$ -l high.c
## specify an email address
#$ -M uname@lbl.gov
## when to send the email when job is (a)borted, (b)egins, (e)nds
#$ -m abe
## specifying an 8 hour runtime
#$ -l h_rt=08:00:00
## specify 48G of memory
#$ -l ram.c=48G
#
# == Your job info goes here
./myprogram inputs
