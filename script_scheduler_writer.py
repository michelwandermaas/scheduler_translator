'''
Author: Michel Wan Der Maas Soares (mwandermaassoares@lbl.gov)

This class is supposed to serve as a mechanism for the developer to write scripts that will work in multiple schedulers.
The project was first developed to work with Univa Grid Engine(UGE) and Simple Linux Utility for Resource Management(SLURM),
but it should be quite easy to implement functionaly with other schedulers.
This is an open-source project, and any development you make to the file will be reviewed and appreciated.
If you want guidelines to include support for other scheduler, do not hesitate to contact me.

Functions whose names start with underscore should not be directly accessed by the user.
'''

import sys

class script_scheduler_writer:
    def __init__(self, scheduler, name = "Name"):
        self.jobsType = []
        self.dependencies = []
        self.dependenciesType = [] #Types: NONE, JOB_NUM, JOB_ID as well as SINGLE or ARRAY.
        self.header = ""
        self.commands = []
        self.name = name
        self.shellSet = False
        self.schedulersSupported = ["UGE","SLURM",""] # "" means run standard syntax, it wont parse the commands.
        self.defaultCommands = ""
        self.defaultHeader = ""
        self.modules = ""
        self._setScheduler(scheduler)
        self.ignoreUnkown = True # ignore unknown commands? if not, delete them.
        self.originalScript = None
        # list of all commands accepted. it will be used to delete unknown commands, and to translate.
        # Dependecies/commands are described in the functions responsible for parsing them.
        self.dependenciesAvail = ["LAST_ADDED","LAST_ADDED_ARRAY", "LAST", "LAST_ID", "LAST_ID_ARRAY", "JOBS_LIST",
                             "JOBS_LIST_ARRAY","ALL_ADDED", "ALL_ADDED_ARRAY"]
        self.commandsAvail = ["JOB_NAME", "RESOURCE_EXCLUSIVE", "RESOURCE_NODES", "RESOURCE_IB", "JOB_ARRAY", "TASK_ID",
                              "RESOURCE_MEM", "RESOURCE_CCM", "RESOURCE_PRIOR_QUEUE"]
    def getJobsSize(self):
        '''
        :return: the amount of jobs appended so far
        '''
        return  self.jobsType.__len__()
    def getSchedulers(self):
        '''
        :return: the list of schedulers currently supported
        '''
        return self.schedulersSupported
    def getScript(self):
        '''
        :return: The script string ready to be written to a file
        '''
        string = ""
        if (not self.shellSet):
            self.setShell("")
        string += self.header
        string += self.defaultHeader +"\n"
        string += self.modules +"\n"
        for x in self.commands:
            string += x
        return string
    def clearCommands(self):
        '''
            Clean all the commands set so far
        '''
        self.commands = []
        self.jobsType = []
        self.dependencies = []
        self.dependenciesType = []
        self.defaultCommands = ""
    def clearAll(self):
        '''
            Clean all variables
        '''
        self.defaultHeader = ""
        self.clearCommands()
        self.header = ""
        self.name = "Name"
        self._setScheduler("")
        self.ignoreUnkown = True
    def _setName(self, name):
        '''
            Set name a name for the object. The name will be used when creating JobID holders in the script.
        '''
        self.name = name
    def _setScheduler(self, type):
        '''
            Sets a scheduler for the script. See this file header for the names of schedulers supported.
        '''
        if (type not in self.schedulersSupported):
            sys.stderr.write("Scheduler not supported.\n")
            sys.exit(1)
        self.scheduler = type
        if(type == "UGE"):
            self.addModule("module load uge\n")
    def setShell(self,shell):
        '''
            Set shell used by the script
        '''
        if (shell != ""):
            shell = shell.replace("\n", "")  # removes any newline characters
            shell = shell.replace("#!", "")  # removes any #! characters
            self.header = "#!"+shell+"\n" + self.header
        else:
            self.header = "#!/bin/bash -l\n" + self.header
        self.shellSet = True
    def addModule(self,module):
        if (module == ""):
            return
        module = module.replace("module ","")
        module = module.split("\n")[0]
        if (self.modules.find(module) >= 0):
            return
        if (module.find("purge") >= 0):
            self.modules = ("module "+module+"\n") + self.modules
            return
        module = "module "+module+"\n"
        self.modules += module

    def addJob(self, command, dependency = "", dependencyType = "", translate = False):
        '''
            Add command to launch a job to the script
        :param command: command to run if first word of command is RUN or launch otherwise (see parseCommand() and getLauncher())
        :param dependency: "LAST_ADDED", "LAST n" (n is a number), "JOB_ID n" (n is the id) (see parseDependency())
        :return: True for success and False for failure
        '''
        if (self.scheduler not in self.schedulersSupported):
            sys.stderr.write("Scheduler not supported.\n")
            sys.exit(1)
        self.jobsType.append([])
        command = command.replace("\n","") #removes any newline characters
        self.commands.append(self._getCommandString(command, dependency, dependencyType, translate))
    def addLineParsed(self, command):
        '''
            Add a line parsing it with the parseCommand function. Used in special cases when one wants to parse a command but not launch a job.
        '''
        if (self.scheduler not in self.schedulersSupported):
            sys.stderr.write("Scheduler not supported.\n")
            sys.exit(1)
        self.jobsType.append([])
        self.commands.append(self._parseCommand(command) + "\n")
    def setDefaultConfig(self, command):
        if (self.scheduler not in self.schedulersSupported):
            sys.stderr.write("Scheduler not supported.\n")
            sys.exit(1)
        command = self._parseCommand(command)
        if (command == ""):
            return
        if (self.scheduler == "SLURM"):
            self.defaultHeader += "#SBATCH "+ command +"\n"
        elif (self.scheduler == "UGE"):
            self.defaultHeader += "#$ " +  command + "\n"
    def unsetDefaultConfig(self):
        self.defaultCommands = ""
    def _getLauncher(self, command):
        '''
            Get launch command based on the type of scheduler. UGE with the command RUN maps to a local run, as well as not specified schedulers.
        :return: launch command or "" for local commands
        '''
        commandList = command.split()
        launcher = ""
        if (commandList[0] == "RUN"):
            if (self.scheduler == "SLURM"):
                launcher = "srun "
                command = command.replace("RUN "," ",1)
            else:
                command = command.replace("RUN ", " ", 1)
        else:
            if (commandList[0] == "LAUNCH" or command.find("LAUNCH ") < 0): #if the first command is LAUNCH or there`s no launch
                command = command.replace("LAUNCH "," ")
                if (self.scheduler == "UGE"):
                    launcher = "qsub "
                elif (self.scheduler == "SLURM"):
                    launcher = "sbatch "
            elif (command.find("LAUNCH ") >= 0): #otherwise, look for a LAUNCH, and replace it with the appropriate launcher.
                if (self.scheduler == "UGE"):
                    launcher = command.split("LAUNCH")[0]+"qsub "
                    command = command.split("LAUNCH")[1]
                elif (self.scheduler == "SLURM"):
                    launcher = command.split("LAUNCH")[0]+"sbatch "
                    command = command.split("LAUNCH")[1]

        return (launcher,command)
    def addEmail(self, email, type):
        '''
            Add email configuration for the jobs in the script
        :param type: "END", "START", "ABORT", "SUSPENDED", "ALWAYS", "NEVER"/"", or a combination separated by a whitespace.
                    Combination of opposites will result in error. ("Always" and "Never")
        '''
        if (self.scheduler not in self.schedulersSupported):
            sys.stderr.write("Scheduler not supported.\n")
            sys.exit(1)
        if (email == "" or email == None):
            return
        if (self.scheduler == "UGE"):
            self.header += "#$ -M "+email+"\n"
            if (type == ""):
                return
            self.header += "#$ -m "
            if(type == "NEVER"):
                self.header += "n\n"
                return
            type = type.split()
            if ("ALWAYS" in  type and "NEVER" in type):
                print("Conflicting email types.\n")
                sys.exit()
            if ("ALWAYS" in type):
                self.header += "beas\n"
                return
            if ("START" in type):
                self.header += "b"
            if ("END" in type):
                self.header += "e"
            if ("ABORT" in type):
                self.header += "a"
            if ("SUSPENDED" in type):
                self.header += "s"
            self.header += "\n"
        elif (self.scheduler == "SLURM"):
            self.header += "#SBATCH --mail-user="+email+"\n"

            self.header += "#SBATCH --mail-type="
            if(type == "NEVER" or type == ""):
                self.header += "NONE\n"
                return
            type = type.split()
            set = False
            if ("ALWAYS" in  type and "NEVER" in type):
                print("Conflicting email types.\n")
                sys.exit()
            if ("ALWAYS" in type):
                self.header += "ALL\n"
                return
            if ("START" in type):
                self.header += "BEGIN"
                set = True
            if ("END" in type):
                if (set):
                    self.header += ","
                self.header += "END"
                set = True
            if ("ABORT" in type or "SUSPENDED" in type):
                if (set):
                    self.header += ","
                self.header += "FAIL"
                set = True
            self.header += "\n"
    def addLineHeader(self, line):
        '''
            Add a line to the header
        '''
        line = line.replace("#", "", 1)  # removes any shebang characters
        self.header += "#"+line
    def addLine(self, line, newline = False):
        '''
            Add a line to the script. By default it does not add a newline character.
            For script translation the default is to add a newline.
        '''
        '''
        if (line.find("module") >= 0):
            list = line.split("module ")
            for x in range(1,list.__len__()):
                self.addModule(list[x])
            line = list[0]
        '''

        if (line == "" or line.replace(" ","") == ""):
            return

        if (newline):
            self.commands.append(line+"\n")
        else:
            self.commands.append(line)
    def addComment(self, comment):
        '''
            Add a comment to the script
        '''

        comment = comment.replace("\n", "")  # removes any newline characters
        comment = comment.replace("#", "")  # removes any shebang characters
        self.commands.append("#"+comment+"\n")
    def _getCommandString(self, command, dependency, dependencyType, translate = False):
        command = self._getLauncher(command)
        ret_string = self.name+"_JOB_"+str(self.jobsType.__len__()) + "=`" + command[0] + self._getDependencyString(dependency, dependencyType) + " " + self._parseCommand(command[1]).replace("\n", "") + "`\n"
        ret_string += self.name+"_JOB_"+str(self.jobsType.__len__()) + "=`echo $" + self.name + "_JOB_" + str(self.jobsType.__len__()) + " | awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}'`\n"
        return ret_string
    def _getDependencyString(self, dependency, dependencyType):
        '''
            Parses dependencies and return the appropriate string according to the scheduler
        :param dependency: string to be parsed
        :return: list of strings to be added
        '''
        dependencyType = dependencyType.replace(" ","")
        self._parseDependency(dependency)
        ret = ""
        if (dependency == ""):
            return ret
        if (self.dependencies[self.jobsType.__len__()-1].__len__()==0):
            return ret
        if(self.scheduler=="UGE"):
            if (self.dependenciesType[self.jobsType.__len__()-1][1] == "SINGLE"):
                ret = "-hold_jid "
            else:
                ret = "-hold_jid_ad "
            bool = False
            for n in self.dependencies[self.jobsType.__len__()-1]:
                if (bool):
                    ret += ","
                if (self.dependenciesType[self.jobsType.__len__()-1][0] == "JOB_NUM"):
                    ret += "$"+self.name+"_JOB_"+str(n)
                else:
                    ret += str(n)
                bool = True
            ret += " "
        elif (self.scheduler=="SLURM"):
            if (dependencyType == "OKAY"):
                ret = "--dependency=afterok:"
            elif (dependencyType == "NOT OKAY"):
                ret = "--dependency=afternotok:"
            elif (dependencyType == "START"):
                ret = "--dependency=after:"
            else:
                ret = "--dependency=afterany:"
            bool = False
            for n in self.dependencies[self.jobsType.__len__()-1]:
                if (bool):
                    ret += ":"
                if (self.dependenciesType[self.jobsType.__len__()-1][0] == "JOB_NUM"):
                    ret += "$"+self.name+"_JOB_"+str(n)
                else:
                    ret += str(n)
                bool = True
            ret += " "
        return ret


    def _parseDependency(self, dependency):
        '''
            Parses dependencies to self.dependency, to be turned into a string later
        :param dependency: string to be parsed
        '''
        '''
        List of constants: (N stands for a number) (More than one kind of dependency will probably cause errors)
            LAST_ADDED : depends on the last job added
            LAST_ADDED_ARRAY : depends on the last job added, and the current job is an array
            LAST N : depends on the last N jobs added
            LAST_ARRAY N : depends on the last N jobs added, and the current job is an array
            JOB_ID N1 N2 N3 N3 : depends on the jobs of ids N1, N2 and so on
            JOB_ID_ARRAY N1 N2 N3 : depends on the jobs of ids N1, N2... and the current job is an array
            JOBS_LIST N1 N2 N3 : depends on the N1th job added, N2th job added, and so on. Jobs index start at 1.
            JOBS_LIST_ARRAY N1 N2 N3 : depends on the N1th job added, N2th job added, and so on. Jobs index start at and the current job is an array.
            ALL_ADDED : depends on all jobs added so far.
            ALL_ADDED_ARRAY : depends on all jobs added so far. The current job must be an array.
        '''
        if (dependency == ""):
            self.dependencies.append([])
            self.dependenciesType.append(("NONE","NONE"))
        else:
            #SINGLE DEPENDENCY
            if (dependency.replace(" ","") == "LAST_ADDED"):
                if (self.jobsType.__len__() == 0):
                    sys.stderr.write("The first job added cannot depend on the last one added.\n")
                    sys.exit()
                else:
                    self.dependenciesType.append(("JOB_NUM", "SINGLE"))
                    self.dependencies.append([self.jobsType.__len__() - 1])
                    return
            if (dependency.replace(" ","") == "LAST_ADDED_ARRAY"):
                if (self.jobsType.__len__() == 0):
                    sys.stderr.write("The first job added cannot depend on the last one added.\n")
                    sys.exit()
                else:
                    self.dependenciesType.append(("JOB_NUM", "ARRAY"))
                    self.dependencies.append([self.jobsType.__len__() - 1])
                    return
            dependency = dependency.split()
            if ("LAST" in dependency):
                pos_dependency = dependency.index("LAST")+1
                num_dependency = int(dependency[pos_dependency])
                self.dependenciesType.append(("JOB_NUM","SINGLE"))
                self.dependencies.append([])
                for x in range(self.jobsType.__len__()-num_dependency, self.jobsType.__len__()):
                    self.dependencies[self.dependencies.__len__()-1].append(x)
            elif ("JOB_ID" in dependency):
                self.dependenciesType.append(("JOB_ID","SINGLE"))
                self.dependencies.append([])
                for x in range(1,dependency.__len__()):
                    if (dependency[x].isdigit()):
                        num_dependency = int(dependency[x])
                    else:
                        num_dependency = dependency[x]
                    self.dependencies[self.dependencies.__len__()-1].append(num_dependency)
            elif ("JOBS_LIST" in dependency or "JOB_LIST" in dependency):
                self.dependencies.append([])
                self.dependenciesType.append(("JOB_NUM","SINGLE"))
                for x in range(1,dependency.__len__()):
                    num_dependency = int(dependency[x])
                    self.dependencies[self.dependencies.__len__()-1].append(num_dependency)
            elif ("ALL_ADDED" in dependency):
                self.dependenciesType.append(("JOB_NUM","SINGLE"))
                self.dependencies.append([])
                for x in range(1, self.jobsType.__len__()):
                    self.dependencies[self.dependencies.__len__()-1].append(x)
            #JOB ARRAYS DEPENDENCY
            elif ("LAST_ARRAY" in dependency):
                pos_dependency = dependency.index("LAST_ARRAY")+1
                num_dependency = int(dependency[pos_dependency])
                self.dependenciesType.append(("JOB_NUM","ARRAY"))
                self.dependencies.append([])
                for x in range(self.jobsType.__len__()-num_dependency, self.jobsType.__len__()):
                    self.dependencies[self.dependencies.__len__()-1].append(x)
            elif ("JOB_ID_ARRAY" in dependency):
                self.dependenciesType.append(("JOB_ID","ARRAY"))
                self.dependencies.append([])
                for x in range(1,dependency.__len__()):
                    num_dependency = int(dependency[x])
                    self.dependencies[self.dependencies.__len__()-1].append(num_dependency)
            elif ("JOBS_LIST_ARRAY" in dependency or "JOB_LIST" in dependency):
                self.dependencies.append([])
                self.dependenciesType.append(("JOB_NUM","ARRAY"))
                for x in range(1,dependency.__len__()):
                    num_dependency = int(dependency[x])
                    self.dependencies[self.dependencies.__len__()-1].append(num_dependency)
            elif ("ALL_ADDED_ARRAY" in dependency):
                self.dependenciesType.append(("JOB_NUM","ARRAY"))
                self.dependencies.append([])
                for x in range(1, self.jobsType.__len__()):
                    self.dependencies[self.dependencies.__len__()-1].append(x)
            else:
                sys.stderr.write("Dependency \""+str(dependency)+"\" not supported.\n")
                sys.exit(1)

    def _deleteOtherOccurances(self, command, occurance, num_args=0):
        if (num_args == 0):
            command = command.replace(occurance, "")
        else:
            # delete additional occurances
            args = 0
            list = command.split()
            auxCommand = ""
            for x in list:
                if x == occurance:  # delete occurrance
                    args = num_args
                elif args > 0:  # delete argument of the additional occurrance
                    args -= 1
                else:
                    auxCommand += x+" "
            command = auxCommand
        return command

    def _parseCommand(self, command): #TODO: ignore unknown commands option (this is currently turned on)
                                     #TODO: add other mem and nodes options
        '''
            Parses the input command looking for certain keywords and replacing them with the appropriate string
        :param command: command to be parsed
        :return: string to be written in the script
        '''
        '''
        List of constants: (N (N1,N2...) stands for a number, and "" stands for a string)
            JOB_NAME "" : sets the name of the job to ""
            RESOURCE_EXCLUSIVE : requests for exclusive nodes
            RESOURCE_NODES N : requests for N nodes
            RESOURCE_IB : requests infiniband resource
            JOB_ARRAY N1:N2 : sets a job array from N1 to N2. (N1 > 0)
            TASK_ID : substituted to the variable set by the scheduler that tells the task id
            RESOURCE_MEM N : requests N amount of memory. Specify either MB or GB right after N. e.g. "RESOURCE_MEM 200MB"
            RESOURCE_CCM : request ccm capabality
            RESOURCE_PRIOR_QUEUE "": requests a certain priority queue
            OUTPUT_CURRENT_DIR : write jobs output to the current directory
        '''
        if (self.scheduler == "UGE"):
            command = command.replace("JOB_NAME ","-N ", 1) # replace the first occurrance
            #delete additional occurances
            command = self._deleteOtherOccurances(command, "JOB_NAME", 1)
        elif (self.scheduler == "SLURM"):
            command = command.replace("JOB_NAME ", "--job-name=", 1)
            command = self._deleteOtherOccurances(command, "JOB_NAME", 1)

        if (self.scheduler == "UGE"):
            command = command.replace("RESOURCE_NODES ","-pe pe_slots ", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_NODES", 1)

        elif (self.scheduler == "SLURM"):
            command = command.replace("RESOURCE_NODES ","-N ", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_NODES", 1)

        if (self.scheduler == "UGE"):
            command = command.replace("RESOURCE_IB","-l infiniband.c=1", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_IB")
        elif (self.scheduler == "SLURM"):
            if (command.find("RESOURCE_IB") >= 0):
                sys.stderr.write("Command RESOURCE_IB not available for SLURM. Ignored.\n")
                command = command.replace("RESOURCE_IB", "")

        if (self.scheduler == "UGE"):
            command = command.replace("RESOURCE_EXCLUSIVE","-l exclusive.c", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_EXCLUSIVE")
        elif (self.scheduler == "SLURM"):
            command = command.replace("RESOURCE_EXCLUSIVE","--exclusive", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_EXCLUSIVE")

        if (self.scheduler == "UGE"):
            command = command.replace("JOB_ARRAY ","-t ", 1)
            command = self._deleteOtherOccurances(command, "JOB_ARRAY", 1)
        elif (self.scheduler == "SLURM"):
            list = command.split()
            auxCommand = ""
            found = False
            for x in list:
                if x == "JOB_ARRAY":
                    auxCommand += "--array="
                    found = True
                elif found:
                    auxCommand += x.replace(":","-",1)
                    break
                else:
                    auxCommand += x+" "
            command = auxCommand
            command = self._deleteOtherOccurances(command, "JOB_ARRAY", 1)

        if (self.scheduler == "UGE"):
            command = command.replace("TASK_ID","$SGE_TASK_ID")
        elif (self.scheduler == "SLURM"):
            command = command.replace("TASK_ID","$SLURM_TASK_ID")

# TW: No support for "-l h_rt"
# TW: This seems not to work...
        if (self.scheduler == "UGE"):
            command = command.replace("RESOURCE_MEM ", "-l ram.c=", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_MEM", 1)
            if (command.find("-l ram.c=") >= 0):
                list = command.split("-l ram.c=")
                listAux = list[1].split(" ")
                listAux[0] = listAux[0].replace("MB","M")
                listAux[0] = listAux[0].replace("GB","G")
                list[1] = " ".join(listAux)
                command = "-l ram.c=".join(list)
        elif (self.scheduler == "SLURM"):
            command = command.replace("RESOURCE_MEM ", "--mem=", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_MEM", 1)

        if (self.scheduler == "UGE"):
            if (command.find("RESOURCE_CCM") >= 0):
                sys.stderr.write("Command RESOURCE_CCM not available for UGE.\n")
                sys.exit(1)
        elif (self.scheduler == "SLURM"):
            command = command.replace("RESOURCE_CCM", "-ccm", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_CCM")

        if (self.scheduler == "UGE"):
            command = command.replace("RESOURCE_PRIOR", "-l", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_PRIOR", 1)
        elif (self.scheduler == "SLURM"):
            command = command.replace("RESOURCE_PRIOR ", "--qos=", 1)
            command = self._deleteOtherOccurances(command, "RESOURCE_PRIOR", 1)

        if (self.scheduler == "UGE"):
            command = command.replace("OUTPUT_CURRENT_DIR", "-cwd", 1)
            command = self._deleteOtherOccurances(command, "OUTPUT_CURRENT_DIR", 1)
        elif (self.scheduler == "SLURM"):
            #ignore, this is the default in SLURM
            command = command.replace("OUTPUT_CURRENT_DIR", "", 1)
            command = self._deleteOtherOccurances(command, "OUTPUT_CURRENT_DIR", 1)

# TW: doesn't support UGE "-v environment_variable=value"
        return command


    def unitTest(self): #TODO: automatize the result checking, instead of prinnting it

        '''
            Test if the returned script is correct.
            This functiom should be used to test the implementation of other scheduler following the pattern set here.
        :return: True if results are correct, False otherwise
        '''

        print "--------------------------------------------------"

        print "Test 1"

        print "--------------------------------------------------"

        # TEST AS LIBRARY
        #---------------------------------------FIRST TEST-----------------------------------------------
        #For reference only, it does not map to anything. The dependencies might not make sense.
        firstExampleScript = \
        """"#/bin/bash\n
            #EMAIL mwandermaassoares@lbl.gov
            #EMAIL_TYPE START END
            JOB_NAME First_Job RESOURCE_NODES 8 ./job1.sh\n
            DEPEND LAST_ADDED JOB_NAME Second_Job JOB_ARRAY 1:10 ./job3.sh\n
            DEPEND LAST 2 JOB_NAME Third_Job JOB_ARRAY 3:25 RESOURCE_IB ./job3.sh\n"""

        #---------------------------------------UGE FIRST TEST___________________________________________
        firstUGEScript = \
        """ #/bin/bash -l\n
            #$ -M mwandermaassoares@lbl.gov\n
            #$ -m be\n
            qsub -N First_Job -pe pe_slots 8 ./job1.sh\n
            qsub -hold_jid First_Job -N Second_Job -t 1:10 ./job2.sh\n
            qsub -hold_jid First_Job Second_Job -N Third_Job -t 3:25 -l infiniband.c=1 ./job3.sh\n"""

        self._setScheduler("UGE")
        self.setShell("/bin/bash -l")
        self.addJob("JOB_NAME First_Job RESOURCE_NODES 8 JOB_NAME RANDOM_JOB ./job1.sh ")
        self.addJob("JOB_NAME Second_Job JOB_ARRAY 1:10 ./job2.sh","LAST_ADDED")
        self.addJob("JOB_NAME Third_Job JOB_ARRAY 3:25 RESOURCE_IB RESOURCE_IB ./job3.sh ", "LAST 2")
        self.addEmail("mwandermaassoares@lbl.gov","START END")
        returnScript = self.getScript()

        print (returnScript)
        print "--------------------------------------------------"

        self.clearAll()

        #---------------------------------------SLURM FIRST TEST---------------------------------------
        firstSLURMScript = \
        """"#/bin/bash -l\n
            #SBATCH --mail-user=mwandermaassoares@lbl.gov
            #SBATCH --mail-type=BEGIN,END
            $Name_JOB_1=`sbatch ./job1.sh -N First_Job -pe pe_slots 8`\n
            $Name_JOB_2=`sbatch ./job2.sh -d afterany:$Name_JOB_1 -N Second_Job --array=1-10`\n
            $Name_JOB_3=`sbatch ./job3.sh -d afterany:$Name_JOB_1:$Name_JOB_2 -N Third_Job -l infiniband.c=1`\n"""

        self._setScheduler("SLURM")
        self.setShell("/bin/bash -l")
        self.addJob("JOB_NAME First_Job RESOURCE_NODES 8 ./job1.sh ")
        self.addJob("JOB_NAME Second_Job JOB_ARRAY 1:10 ./job2.sh ","LAST_ADDED")
        self.addJob("JOB_NAME Third_Job JOB_ARRAY 3:25 RESOURCE_IB ./job3.sh ", "LAST 2")
        self.addEmail("mwandermaassoares@lbl.gov","START END")
        returnScript = self.getScript()

        print (returnScript)

        print "--------------------------------------------------"

        self.clearAll()

        print "Test 2"

        print "--------------------------------------------------"

        #---------------------------------------SECOND TEST-----------------------------------------------
        #For reference only, it does not map to anything. The dependencies might not make sense.
        secondExampleScript = \
        """"#/bin/bash\n
            #EMAIL mwandermaassoares@lbl.gov\n
            #EMAIL_TYPE END ABORT START\n
            JOB_NAME First_Job RESOURCE_NODES 8 RESOURCE_EXCLUSIVE ./job1.sh \n
            LAST_ADDED JOB_NAME Second_Job JOB_ARRAY 1:10 ./job2.sh \n
            LAST_ADDED_ARRAY JOB_NAME Third_Job JOB_ARRAY 3:25 RESOURCE_IB ./job3.sh \n
            LAST_ARRAY 2 JOB_NAME Fourth_Job JOB_ARRAY 1:1000 RESOURCE_NODES 16 ./job4.sh """

        #---------------------------------------UGE SECOND TEST___________________________________________
        secondUGEScript = \
        """"#/bin/bash -l\n
            #$ -M mwandermaassoares@lbl.gov\n
            #$ -m eab\n
            $Name_JOB_1=`qsub -N First_Job -pe pe_slots 8 -l exclusive.c ./job1.sh `\n
            $Name_JOB_2=`qsub -hold_jid $Name_JOB_1 -N Second_Job -t 1:10 ./job2.sh `\n
            $Name_JOB_3=`qsub -hold_jid_ad $Name_JOB_2 -N Third_Job -t 3:25 -l infiniband.c=1 ./job3.sh `\n
            $Name_JOB_4=`qsub -hold_jid_ad $Name_JOB_2,$Name_JOB_3 -N Fourth_Job -t 1:1000 -pe pe_slots 16 ./job4.sh `"""

        self._setScheduler("UGE")
        self.setShell("/bin/bash -l")
        self.setDefaultConfig("RESOURCE_MEM 200MB RESOURCE_NODES 1")
        self.addJob("JOB_NAME First_Job RESOURCE_NODES 8 RESOURCE_EXCLUSIVE ./job1.sh ")
        self.addJob("JOB_NAME Second_Job JOB_ARRAY 1:10 ./job2.sh ","LAST_ADDED")
        self.addJob("JOB_NAME Third_Job JOB_ARRAY 3:25 RESOURCE_IB ./job3.sh ", "LAST_ADDED_ARRAY")
        self.addJob("JOB_NAME Fourth_Job JOB_ARRAY 1:1000 RESOURCE_NODES 16 ./job4.sh ", "LAST_ARRAY 2")
        self.addEmail("mwandermaassoares@lbl.gov","END ABORT START")
        returnScript = self.getScript()

        print (returnScript)

        print "--------------------------------------------------"

        self.clearAll()

        #---------------------------------------SLURM SECOND TEST___________________________________________
        secondSLURMcript = \
        """"#/bin/bash -l\n
            #$ -M mwandermaassoares@lbl.gov\n
            #$ -m eab\n
            $Name_JOB_1=`sbatch --job-name=First_Job -ntasks-per-node=8 -l exclusive.c ./job1.sh `\n
            $Name_JOB_2=`sbatch -d afterany:$Name_JOB_1 --job-name=Second_Job --array=1-10 ./job2.sh `\n
            $Name_JOB_3=`sbtach -d afterany:$Name_JOB_2 -job-name=Third_Job --array:3-25 --contraint=IB ./job3.sh `\n
            $Name_JOB_4=`sbatch -d afterany:$Name_JOB_2:$Name_JOB_3 --job-name=Fourth_Job --array=1-1000 -pntasks-per-node=16 ./job4.sh `"""

        self._setScheduler("SLURM")
        self.setShell("/bin/bash -l")
        self.setDefaultConfig("RESOURCE_MEM 200MB RESOURCE_NODES 1")
        self.addJob("JOB_NAME First_Job RESOURCE_NODES 8 RESOURCE_EXCLUSIVE ./job1.sh ")
        self.addJob("JOB_NAME Second_Job JOB_ARRAY 1:10 ./job2.sh ","LAST_ADDED")
        self.addJob("JOB_NAME Third_Job JOB_ARRAY 3:25 RESOURCE_IB ./job3.sh ", "LAST_ADDED_ARRAY")
        self.addJob("JOB_NAME Fourth_Job JOB_ARRAY 1:1000 RESOURCE_NODES 16 ./job4.sh ", "LAST_ARRAY 2")
        self.addEmail("mwandermaassoares@lbl.gov","END ABORT START")
        returnScript = self.getScript()

        print (returnScript)

        print "--------------------------------------------------"

        self.clearAll()

        return True

if __name__ == "__main__":
    # run unit test
    test = script_scheduler_writer("")
    test.unitTest()
