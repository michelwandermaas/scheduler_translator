#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -cwd -l h_rt=24:00:00 -l ram.c=100G 


#
# Set SGE options:
#
# run the job in the current working directory (where qsub is called)
# specify an email address
# specify when to send the email when job is (a)borted, (b)egins, or (e)nds
# specify a 24 hour runtime
# specify the memory used, with ram.c
# Your job info goes here
./myprogram inputs

