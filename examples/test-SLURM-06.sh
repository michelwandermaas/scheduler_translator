#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -S /bin/bash -cwd -v env_var_name=value -l h_rt=12:30:00 -l exclusive.c -w e 


#
# == Set SGE options:
#
# -- ensure BASH is used
# -- run the job in the current working directory (where qsub is called)
# -- run with the environment variables from the User's environment
# -- specify an email address
# -- specify when to send the email when job is (a)borted,
# -- (b)egins or (e)nds
# -- specifying a 12 hour 30 minute runtime
# -- request a whole node
# -- Use the following, so you can catch the errors thrown by SGE if your job fails
# -- to run.
#
# -- run a job with 16 threads, this is an example with OpenMP
# NOTE: You do NOT need to specify a parallel environment.
# == Your job info goes here
export OMP_NUM_THREADS=16
./myprogram inputs

