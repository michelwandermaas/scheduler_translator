#!/bin/bash
#
# == Set SGE options:
#
# -- ensure BASH is used
# -- run the job in the current working directory (where qsub is called)
#$ -cwd
# -- run with the environment variables from the User's environment
#$ -v env_var_name=value
# -- specify an email address
#$ -M uname@lbl.gov
# -- specify when to send the email when job is (a)borted,
# -- (b)egins or (e)nds
#$ -m abe
# -- specifying a 24 hour runtime
#$ -l h_rt=24:00:00
# -- Use the following, so you can catch the errors thrown by SGE if your job fails
# -- to run.
#$ -w e
####
# -- request 4 slots on the same node, -pe is the flag for parallel environment, pe_slots is the basic
# -- parallel environment on Genepool.
#$ -pe pe_slots 4
# -- request 10GB of memory per slot, for a total of 10*4= 40GB
#$ -l ram.c=10G
# == Your job info goes here
./myprogram inputs
