import os,csv,re
import numpy as np

'''
Logger class to handle the logging tasks of the pipline software
project logfile - main log file that holds project specific history and variable information
model logfiles - each run of a model results in a results pickle as well as a log file
figure logfiles - figures may be manipulated after the run of a model -- those manipulations are documented here

'''

class Logger():
    
    ## consttructor
    def __init__(self):
        self.log = {'currentState':'initial'}

    def initialize(self,projectID,homeDir,load=False):
        self.projectID = projectID
        self.homeDir = homeDir
        self.modelDir = os.path.join(self.homeDir,'models')
        self.figDir  = os.path.join(self.homeDir, 'figs')
        self.dataDir = os.path.join(self.homeDir, 'data')

        if load == False:
            self.log = self.set_var_defaults()
        elif load == True:
            self.log = self.read_project_log()

    def set_var_defaults(self):
        log = {}
        log['currentState'] = 'Data Processing'
        log['highestState'] = 0
        log['subsample'] = '1e3'
        log['processingChannels'] = None
        log['selectedList'] = None
        log['selectedModel'] = None
        log['modelToRun'] = None
        log['transform'] = None
        log['resultsMode'] = 'modes'
        log['componentStates'] = None
        log['numComponents'] = 16
        log['dataProcessingAction'] = 'channel select'
        log['checksArray'] = None
        log['excludedFilesQA'] = []
        log['excludedFilesAnalysis'] = []
        log['excludedChannels'] = []

        return log

    ## effectivly the only action necessary to save a project in its current state
    def write(self):
        writer = csv.writer(open(os.path.join(self.homeDir,self.projectID+'.log'),'w'))
        
        for key,item in self.log.iteritems():
            writer.writerow([key,item])
            
    ## reads the log file assciated with the current project and returns a dict
    def read_project_log(self):
        projLog = os.path.join(self.homeDir,self.projectID+".log")

        if os.path.isfile(projLog) == False:
            print "ERROR: invalid model logfile specified",projLog
            return None
        else:
            logFileDict = {}
            reader = csv.reader(open(projLog,'r'))
            for linja in reader:

                if linja[0] == 'checksArray':
                    linja[1] = self.str2array(linja[1])

                logFileDict[linja[0]] = linja[1]
            
                if linja[0] == 'excludedFilesQA' or linja[0] == 'excludedChannels' or linja[0] == 'excludedFilesAnalysis':
                    linja[1] = re.sub("\s+|\[|\]|'","",linja[1]).split(",")

            return logFileDict

    ## given a model name read in a model log file and return a dictionary
    def read_model_log(self,modelName):
        longName = os.path.join(self.modelDir,modelName+".log")
        if os.path.isfile(longName) == False:
            print "ERROR: invalid model logfile specified",longName
            return None
        else:
            logFileDict = {}
            reader = csv.reader(open(longName,'r'))
            for linja in reader:
                logFileDict[linja[0]] = linja[1]
                  
            return logFileDict

    def str2array(self,myStr):
        if not re.search("^\[\[",myStr):
            return None

        myStr = myStr[1:-1]
        myStr = re.sub("\n", ",", myStr)
        myList = myStr.split(",")
        newList = []

        for l in myList:
            newList.append([int(float(i)) for i in re.sub("\[|\]","",l).split()])

        return np.array(newList)

    def str2list(self,myStr):
        if not re.search("^\[\[",myStr):
            return None

        myStr = myStr[1:-1]
        myStr = re.sub("\n", ",", myStr)
        myList = myStr.split(",")
        newList = []

        for l in myList:
            newList.append([int(float(i)) for i in re.sub("\[|\]","",l).split()])

        return newList

