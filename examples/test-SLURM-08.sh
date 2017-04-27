#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -cwd -v env_var_name=value -l h_rt=24:00:00 -w e -pe pe_slots 4 -l ram.c=10G 


#
# == Set SGE options:
#
# -- ensure BASH is used
# -- run the job in the current working directory (where qsub is called)
# -- run with the environment variables from the User's environment
# -- specify an email address
# -- specify when to send the email when job is (a)borted,
# -- (b)egins or (e)nds
# -- specifying a 24 hour runtime
# -- Use the following, so you can catch the errors thrown by SGE if your job fails
# -- to run.
#
# -- request 4 slots on the same node, -pe is the flag for parallel environment, pe_slots is the basic
# -- parallel environment on Genepool.
# -- request 10GB of memory per slot, for a total of 10*4= 40GB
# == Your job info goes here
./myprogram inputs

