#!/bin/bash
#
# == Set SGE options:
#
# -- ensure BASH is used
#$ -S /bin/bash
# -- run the job in the current working directory (where qsub is called)
#$ -cwd
# -- run with the environment variables from the User's environment
#$ -v env_var_name=value
# -- specify an email address
#$ -M uname@lbl.gov
# -- specify when to send the email when job is (a)borted,
# -- (b)egins or (e)nds
#$ -m abe
# -- specifying a 12 hour 30 minute runtime
#$ -l h_rt=12:30:00
# -- request a whole node
#$ -l exclusive.c
# -- Use the following, so you can catch the errors thrown by SGE if your job fails
# -- to run.
#$ -w e
####
# -- run a job with 16 threads, this is an example with OpenMP
# NOTE: You do NOT need to specify a parallel environment.
# == Your job info goes here
export OMP_NUM_THREADS=16
./myprogram inputs
