#!/usr/bin/env python
'''
Author: Michel Wan Der Maas Soares (mwandermaassoares@lbl.gov)
'''
import script_scheduler_writer
import sys


class translator:
    def __init__(self, script, scheduler_in, scheduler_out, force=False, ignore=False, name="Name"):
        self.scriptWriter = script_scheduler_writer.script_scheduler_writer(scheduler_out, name)
        self.originalScript = script
        self.scheduler_in = scheduler_in
        self.scheduler_out = scheduler_out
        self.force = force
        self.ignore = ignore
        self.listAvailUGECommands = ["-N", "-pe", "-l", "-t"]  # commands currently supported
        self.listAvailUGEDepend = ["-hold_jid", "-hold_jid_ad"]

    def _inputScript(self, script):
        self.originalScript = script

    def getScript(self):
        self._translate()
        return self.scriptWriter.getScript()

    def _parseUGECommand(self, command, force = False):
        '''
        :param command: command to be parsed
        :return: command parsed
        '''
        '''
            Development comment:
                This function is the inverse of parseCommand, and it was written basically swapping the 1st and 2nd argument
                of the replace function. It assumes the original script is correct, so there isn`t any error checking.
        '''

        if (self.ignore == True):
            for x in command.split():
                if (x.startswith("-") and (x not in self.listAvailUGECommands and x not in self.listAvailUGEDepend)):
                    sys.stderr.write("Command \"" + x + "\" not supported. Deleted.\n")
                    command = command.replace(x, "")
        elif (self.force == False and force == False):
            for x in command.split():
                if (x.startswith("-") and (x not in self.listAvailUGECommands and x not in self.listAvailUGEDepend)):
                    sys.stderr.write("Command \"" + x + "\" not supported. Use --helpUGE to see all the supported commands or --force to ignore unknown commands.\n")
                    exit(1)

        command = command.replace("-N ", "JOB_NAME ", 1)  # replace the first occurrance

        command = command.replace("-pe pe_slots ", "RESOURCE_NODES ", 1)

        command = command.replace("-l infiniband.c=1", "RESOURCE_IB", 1)

        command = command.replace("-l exclusive.c", "RESOURCE_EXCLUSIVE", 1)

        command = command.replace("-t ", "JOB_ARRAY ", 1)

        command = command.replace("$SGE_TASK_ID", "TASK_ID", 1)

        command = command.replace("-l ram.c=", "RESOURCE_MEM ", 1)

        command = command.replace("-l", "RESOURCE_PRIOR", 1)

        return command

    def _parseUGEdependencies(self, dependencies, type, nameJobs):
        '''
        :param dependencies: the word following -hold_jid or -hold_jid_ad
        :return:
        '''
        retString = ""
        dependencies = dependencies.split(",")  # separate dependencies
        depJobId = []
        depJobList = []
        depJobIdArray = []
        depJobListArray = []
        for d in dependencies:
            if (d.startswith("$")):  # ignore, it is an enviroment variable
                if (type == "ARRAY"):
                    depJobIdArray.append(d)
                else:
                    depJobId.append(d)
                continue
            else:  # check if it the name of a job launched so far
                nameFound = False
                for n in range(0, nameJobs.__len__()):
                    x = nameJobs[n]
                    name = d.replace("\"", "")
                    name = name.replace("*", "")
                    if d == x[0]:
                        if (type == "ARRAY"):
                            depJobListArray.append(nameJobs[n][1])
                            nameFound = True
                            break
                        else:
                            depJobList.append(nameJobs[n][1])
                            nameFound = True
                            break
                    elif (x[0].startswith(name)):
                        if (type == "ARRAY"):
                            depJobListArray.append(nameJobs[n][1])
                            nameFound = True
                            break
                        else:
                            depJobList.append(nameJobs[n][1])
                            nameFound = True
                            break
                if (nameFound):
                    break
            if (d.isdigit()):  # check if it made of numbers only, treat it as a job_id
                if (type == "ARRAY"):
                    depJobIdArray.append(d)
                else:
                    depJobId.append(d)
            elif (not self.ignore):  # it is probably the name of some other job, and this is not allowed in SLURM. Exit with error.
                sys.stderr.write("Invalid dependency: \"" + d + "\". Keep in mind names of jobs launched in other scripts are not allowed. See --helpUGE for options.\n")
                sys.exit(1)
            else:
                sys.stderr.write("Dependency \"" + d + "\" ignored.\n")
        if (depJobId.__len__() > 0):
            retString += "JOB_ID " + ",".join(depJobId)
        if (depJobList.__len__() > 0):
            retString += "JOB_LIST " + ",".join(depJobList)
        if (depJobIdArray.__len__() > 0):
            retString += "JOB_ID_ARRAY " + ",".join(depJobId)
        if (depJobListArray.__len__() > 0):
            retString += "JOB_LIST_ARRAY " + ",".join(depJobList)
        return retString

    def _parseUGEEmail(self, type):
        ret = ""
        if (type == ""):
            return ret
        if (type == "n"):
            ret = "NEVER "
            return ret
        type = type.split()
        if ("abe" in type or "ae" in type):
            ret = "ALWAYS "
            return ret
        if ("b" in type):
            ret += "START "
        if ("e" in type):
            ret += "END "
        if ("a" in type):
            ret += "ABORT"
        if ("s" in type):
            ret += "SUSPENDED"
        return ret

    def _translate(self):
        if (self.scheduler_out not in self.scriptWriter.schedulersSupported):
            sys.stderr.write("Scheduler not supported.")
            sys.exit(1)
        if (self.scheduler_in == ""):  # direct translation from standard syntax to the scheduler
            self.scriptWriter.scheduler = self.scheduler_out
            for line in self.originalScript:
                auxLine = line.split()  # remove whitespaces and newlines
                space = " "
                if (not auxLine):
                    continue
                if (auxLine[0].upper() == "SHELL"):
                    auxLine.pop(0)
                    self.scriptWriter.setShell(space.join(auxLine))
                elif (auxLine[0].upper() == "COMMENT"):
                    auxLine.pop(0)
                    self.scriptWriter.addComment(space.join(auxLine))
                elif (auxLine[0].upper() == "EMAIL"):
                    auxLine.pop(0)
                    self.scriptWriter.addEmail(auxLine[0], auxLine[1])
                elif (auxLine[0].upper() == "DEFAULT_CONFIG"):
                    auxLine.pop(0)
                    self.scriptWriter.setDefaultConfig(space.join(auxLine))
                elif (auxLine[0].upper() == "JOB"):
                    auxLine.pop(0)
                    newString = space.join(auxLine)
                    index = newString.find("DEPEND")
                    if (index == -1):
                        self.scriptWriter.addJob(newString)
                    else:
                        newString = newString.split("DEPEND ")
                        if (newString[1].find("DEPEND_TYPE") != -1):
                            newString[1] = newString[1].split("DEPEND_TYPE")
                            self.scriptWriter.addJob(newString[0], newString[1][0], newString[1][1])
                        else:
                            s = newString[1]
                            self.scriptWriter.addJob(newString[0], s)
                elif (auxLine[0].upper() == "LINE"):
                    auxLine.pop(0)
                    self.scriptWriter.addLine(space.join(auxLine), True)
                elif (auxLine[0].upper() == "LINE_PARSED"):
                    auxLine.pop(0)
                    self.scriptWriter.addLineParsed(space.join(auxLine))
                else:
                    sys.stderr.write("Unknown command: \"" + auxLine[0] + "\". Use --help to see available options.\n")
                    sys.exit(1)
        elif (self.scheduler_in == "UGE"):
            parseCommandFunction = self._parseUGECommand
            parseDependencyFunction = self._parseUGEdependencies
            parseEmail = self._parseUGEEmail
            formatLauncher = "qsub"
            formatMail = "-M"
            formatMailType = "-m"
            formatName = "-N"
            formatDependency = "-hold_jid"
            formatDependencyArray = "-hold_jid_ad"
            formatDefaultConfig = "#$"

            self.scriptWriter.scheduler = self.scheduler_out

            email = ""
            emailType = ""
            default_config = ""
            nameJobs = []
            for line in self.originalScript:
                if (line==""):
                    continue
                shellIndex = line.find("#!")
                if (shellIndex != -1):  # setting shell
                    self.scriptWriter.setShell(line)
                else:
                    if (line.startswith(formatDefaultConfig)):  # default_config
                        auxLine = line.replace("\n","")
                        if (line.find(formatMail) != -1):  # search for formatMail, if found it is an email header
                            list = line.split(formatMail+" ")
                            email = list[1].split()[0]
                            email = email.replace("\n", "")
                            auxLine = auxLine.replace(formatMail, "")
                            auxLine = auxLine.replace(email, "")
                        if (auxLine.find(formatMailType) != -1):  # search for formatMailType, if found it is an email type header
                            list = auxLine.split(formatMailType+" ")
                            emailType = list[1].split()[0]
                            auxLine = auxLine.replace(emailType, "")
                            emailType = parseEmail(emailType.replace(" ", ""))
                            auxLine = auxLine.replace(formatMailType, "")
                        auxLine = auxLine.replace("\n", "")
                        if (auxLine.replace(" ","") != ""):
                            default_config += auxLine.split(formatDefaultConfig)[1]
                    elif (line[0] == "#"):  # this is a comment
                        self.scriptWriter.addComment(line)
                    else:  # either a JOB, LINE or LINE_PARSED
                        qsubIndex = line.find(formatLauncher)
                        if (qsubIndex != -1):  # it is a job
                            line = line.replace(formatLauncher + " ", "LAUNCH ")
                            if (line.find(formatName)):
                                name = line.split(formatName)[1].split()[0]  # argument right after formatName, if found
                                nameJobs.append((name, str(nameJobs.__len__()+1)))
                            else:
                                nameJobs.append(("", str(nameJobs.__len__()+1)))
                            line = parseCommandFunction(line)
                            # find formatDependency or formatDependencyArray, take it out, get word after the command, parse dependency
                            if (line.find(formatDependencyArray) != -1):
                                list = line.split(formatDependencyArray)
                                dependency = list[1].split()[0]  # first word after formatDependencyArray
                                line = line.replace(formatDependencyArray, "")
                                line = line.replace(dependency, "")
                                dependency = parseDependencyFunction(dependency, "ARRAY", nameJobs)
                                self.scriptWriter.addJob(line, dependency, "", True)
                            if (line.find(formatDependency) != -1):
                                list = line.split(formatDependency)
                                dependency = list[1].split()[0]  # first word after formatDependency
                                line = line.replace(formatDependency, "")
                                line = line.replace(dependency, "")
                                dependency = parseDependencyFunction(dependency, "SINGLE", nameJobs)
                                self.scriptWriter.addJob(line, dependency, "", True)
                            else:
                                self.scriptWriter.addJob(line, "", "", True)
                        else:
                            newLine = parseCommandFunction(line, True)
                            self.scriptWriter.addLine(newLine)
            # add email and default configurations
            self.scriptWriter.addEmail(email, emailType)
            self.scriptWriter.setDefaultConfig(default_config)
        else:
            sys.stderr.write("Translation not currently supported.\n")
            sys.exit(1)

    def unitTest(self, listOfScripts, verbose = False):
        # TEST AS DIRECT SCRIPT INPUT
        # ---------------------------------------FIRST TEST-----------------------------------------------

        # Test translating from standard syntax to every scheduler
        firstExampleScript = listOfScripts[0]
        scriptsList = {}
        for s in self.scriptWriter.schedulersSupported:
            if (s != ""):
                sys.stderr.write("Translation from standard syntax to " + s + ".\n")
                writerTest = translator(firstExampleScript, "", s)
                script = writerTest.getScript()
                scriptsList[s] = script.split("\n")
                if(verbose):
                    print script
                sys.stderr.write("Translation finished.\n")
        # Test translating from every scheduler to any other
        for s_in in self.scriptWriter.schedulersSupported:
            for s_out in self.scriptWriter.schedulersSupported:
                if (s_in != "" and s_out != "" and s_in != s_out):
                    sys.stderr.write("Translation from "+s_in+" to "+s_out+".\n")
                    writerTest = translator(scriptsList.get(s_in), s_in, s_out)
                    script = writerTest.getScript()
                    if (verbose):
                        print script+"\n\n"
                    sys.stderr.write("Translation finished.\n")
        return True


def displayHelp(writer, full=True):
    help = \
        "\nThis program takes as input a script, and translate all the scheduler-specific commands to whichever " \
        + "scheduler you would like. Currently it supports: "
    list = []
    for s in writer.scriptWriter.schedulersSupported:
        if s != "":
            list.append(s)
    help += ",".join(list) + ".\n"
    if (full):
        help += "You can also see specific help for your scheduler using: "
        list = []
        for s in writer.scriptWriter.schedulersSupported:
            if s != "":
                list.append("--help" + s)
        help += ",".join(list) + ".\n"
    help += "\nAuthor: Michel Wan der Maas Soares(mwandermaassoares@lbl.gov)\n\n"
    help += "Options: \n"
    help += "--force: write unknown commands and dependencies\n"
    help += "--ignore ignore/delete unknown commands and dependencies"

    return help+"\n"


def displayUsage():
    sys.stderr.write("Usage: translate_script.py FILE -i SCHEDULER_IN -o SCHEDULER_OUT [options]\n")
    sys.stderr.write("For stdin, please specify 'stdin' instead of FILE.\n")
    sys.stderr.write("If either -s or -o is not specified, it will assume standard syntax. You have to specify one of the two.\n")
    sys.stderr.write("Use --help to see the available options and schedulers.\n")


def main():
    writer = translator("", "", "")
    if len(sys.argv) < 4 or len(sys.argv) > 7:
        for x in range(1,len(sys.argv)):
            if (sys.argv[x] == "--help"):
                print displayHelp(writer)
                sys.exit(0)
            elif (sys.argv[x] == "--helpUGE"):
                print displayHelp(writer, False)
                print "Supported commands for UGE:"
                print ",".join(writer.listAvailUGECommands) + ".\n"
                sys.exit(0)
            elif (sys.argv[x] == "--develop_TEST"):
                writer = translator("", "", "")
                dir = ""
                if (x + 1 < len(sys.argv)):
                    dir = sys.argv[x+1]
                file = "firstExampleScript.txt"
                try:
                    with open(dir + file) as f:
                        firstExampleScript = f.readlines()
                    if (writer.unitTest([firstExampleScript])):
                        print ("The test was successful.\n")
                    else:
                        print ("The test failed.\n")
                except IOError:
                    sys.stderr.write("Cannot open file: " + file + "\n")
                    displayUsage()
                    sys.exit(-1)
                sys.exit(0)
            elif (sys.argv[x] == "--develop_TEST_verbose"):
                writer = translator("", "", "")
                dir = ""
                if (x + 1 < len(sys.argv)):
                    dir = sys.argv[x+1]
                file = "firstExampleScript.txt"
                try:
                    with open(dir + file) as f:
                        firstExampleScript = f.readlines()
                    if (writer.unitTest([firstExampleScript], True)):
                        print ("The test was successful.\n")
                    else:
                        print ("The test failed.\n")
                    sys.exit(0)
                except IOError:
                    sys.stderr.write("Cannot open file: " + file + "\n")
                    displayUsage()
                    sys.exit(-1)
        displayUsage()
    else:
        file = sys.argv[1]
        scheduler_in = ""
        scheduler_out = ""
        force = False
        ignore = False
        for x in range(2, len(sys.argv)):
            if (sys.argv[x] == "-i"):
                if (x + 1 < len(sys.argv)):
                    scheduler_in = sys.argv[x + 1]
                else:
                    sys.stderr.write("Scheduler type for the input not specified")
                    displayUsage()
                    sys.exit(1)
            elif (sys.argv[x] == "-o"):
                if (x + 1 < len(sys.argv)):
                    scheduler_out = sys.argv[x + 1]
                else:
                    sys.stderr.write("Scheduler type for the output not specified")
                    displayUsage()
                    sys.exit(1)
            elif (sys.argv[x] == "--force"):
                force = True
            elif (sys.argv[x] == "--ignore"):
                ignore = True
        if (file == "stdin"):
            with sys.stdin as f:
                inputList = f.readlines()
        else:
            try:
                with open(file) as f:
                    inputList = f.readlines()
            except IOError:
                sys.stderr.write("Cannot open file: "+file+"\n")
                displayUsage()
                sys.exit(-1)
        name = file.split(".")
        name = name[0].replace(" ","")
        name = name.split("/")
        name = name[name.__len__()-1]
        writer = translator(inputList, scheduler_in, scheduler_out, force, ignore, name)
        print (writer.getScript())


if __name__ == "__main__":
    main()
