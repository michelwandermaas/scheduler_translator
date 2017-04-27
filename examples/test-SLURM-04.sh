#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -cwd -l high.c -l h_rt=08:00:00 -l ram.c=48G 


#
# == Set SGE options:
#
# run the job in the current working directory (where qsub is called)
# submit the job to the high priority queue
# specify an email address
# when to send the email when job is (a)borted, (b)egins, (e)nds
# specifying an 8 hour runtime
# specify 48G of memory
#
# == Your job info goes here
./myprogram inputs

