#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -cwd -l exclusive.c -l h_rt=12:00:00 -l ram.c=120G 



#
# Set SGE options:
#
# run the job in the current working directory (where qsub is called)
# specify an email address
# specify when to send the email when job is (a)borted, (b)egins, or (e)nds
# Request a whole compute node, the new hardware is all scheduled this way
# specify a 12 hour runtime
# specify the memory used, up to 120G of memory with ram.c

# Your job info goes here
./myprogram inputs

