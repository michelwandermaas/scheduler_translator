#!/bin/bash
#SBATCH --mail-user=uname@lbl.gov
#SBATCH --mail-type=ALL
#SBATCH -cwd -v env_var_name=value -l h_rt=12:00:00 -w e -pe pe_slots 4 


#
# == Set SGE options:
#
# -- ensure BASH is used
# -- run the job in the current working directory (where qsub is called)
# -- run with the environment variables from the User's environment
# -- specify an email address
# -- specify when to send the email when job is (a)borted,
# -- (b)egins or (e)nds
# -- specifying a 12 hour runtime
# -- Use the following, so you can catch the errors thrown by SGE if your job fails
# -- to submit.
#
# -- request 4 slots on the same node, it will get 5GB memory per slot for a total of 20GB
# -- for the entire job.  -pe is the flag for parallel environment, pe_slots is the basic
# -- parallel environment on Genepool.
# == Your job info goes here
./myprogram inputs

