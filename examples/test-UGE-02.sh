#!/bin/bash

#
# Set SGE options:
#
## run the job in the current working directory (where qsub is called)
#$ -cwd
## specify an email address
#$ -M uname@lbl.gov
## specify when to send the email when job is (a)borted, (b)egins, or (e)nds
#$ -m abe
## Request a whole compute node, the new hardware is all scheduled this way
#$ -l exclusive.c
## specify a 12 hour runtime
#$ -l h_rt=12:00:00
## specify the memory used, up to 120G of memory with ram.c
#$ -l ram.c=120G

# Your job info goes here
./myprogram inputs
