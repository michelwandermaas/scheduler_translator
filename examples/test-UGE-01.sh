#!/bin/bash
# Set SGE options:
## ensure a specific environment variable is set properly
#$ -v env_var=<value>
## run the job in the current working directory (where qsub is called)
#$ -cwd
## specify an email address
#$ -M uname@lbl.gov
## specify when to send the email when job is (a)borted, (b)egins or (e)nds normally
#$ -m abe
## Specify a run time of 11 hours (or 39600 seconds)
#$ -l h_rt=11:00:00
## Specify 12G of memory for the job
#$ -l ram.c=12G

## Your job info goes here
./myprogram inputs
