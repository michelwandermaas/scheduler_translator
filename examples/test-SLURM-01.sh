#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -v env_var=<value> -cwd -l h_rt=11:00:00 -l ram.c=12G 


# Set SGE options:
# ensure a specific environment variable is set properly
# run the job in the current working directory (where qsub is called)
# specify an email address
# specify when to send the email when job is (a)borted, (b)egins or (e)nds normally
# Specify a run time of 11 hours (or 39600 seconds)
# Specify 12G of memory for the job

# Your job info goes here
./myprogram inputs

