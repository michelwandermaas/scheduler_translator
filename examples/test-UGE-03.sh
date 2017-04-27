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
## specify a 24 hour runtime
#$ -l h_rt=24:00:00
## specify the memory used, with ram.c
#$ -l ram.c=100G
## Your job info goes here
./myprogram inputs
