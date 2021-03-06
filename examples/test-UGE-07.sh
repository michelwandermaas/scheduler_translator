#!/bin/bash
#
# == Set SGE options:
#
# -- run the job in the current working directory (where qsub is called)
#$ -cwd
# -- run with the environment variables from the User's environment
#$ -v env_var_name=value
# -- Specify the memory per MPI task to 120G
#$ -l ram.c=120G
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
# -- The parallel environment is specified with the -pe flag. The following
# -- requests 2 nodes with one MPI task per node
#$ -pe pe_1 2
# -- The following would request 4 16 core nodes with 16 MPI tasks per node
##$ -pe pe_16 64
# -- The following would request 6 8 core nodes with 8 MPI tasks per node
##$ -pe pe_8 48
# == Your job info goes here
module load openmpi/1.8.1
# -- Using mpirun in OpenMPI 1.8 involves mapping processes across processing devices.
# -- Here we use ppr (processes per resource).
mpirun --map-by ppr:1:node --np 2 ./myprogram inputs
