'''
Controller.py

This program or module is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 2 of the License, or
version 3 of the License, or (at your option) any later version. It is
provided for educational purposes and is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
the GNU General Public License for more details.
Adam Richards                                                                                                                                                                                                                              
adamricha@gmail.com     

A. Richards

'''

import csv,sys,time,re,shutil
import numpy as np
from PIL import Image

try:
    from PyQt4 import QtGui, QtCore
except:
    print "IMPORT WARNING: Module PyQt4 is not available"
    sys.exit()

try:
    from config_cs import configCS
    pythonPath = configCS['pythonPath']
except:
    pythonPath = 'python'

import re,os,sys,csv,webbrowser,cPickle
from Model import Model
import subprocess
from gdiqt4 import get_gene_list_names
from Logging import Logger

class Controller:
    def __init__(self,viewType=None):
        '''
        construct an instance of the controller class
        to use invoke the method initialize
        '''
        ## determine location                                                            
        cwd = os.getcwd()

        if os.path.split(cwd)[1] == 'gdiqt4':
            self.baseDir = cwd
        elif os.path.split(cwd)[1] == 'tests':
            self.baseDir = os.path.join(os.path.split(cwd)[0],'gdiqt4')
        else:
            print "ERROR: cannot determine current working directory"

        ## basic application wide variables 
        self.viewType = viewType
        self.appName = "Gene Data Integrator"
        self.fontName = 'Arial' #'Helvetica'
        self.verbose = True
        self.reset_workspace()

    def reset_workspace(self):
        self.projectID = None
        self.homeDir = None
        self.model = Model()
        self.log = Logger()
        self.subsampleIndices = None
                              
    def save(self):
        self.log.write()

    def initialize_project(self,projectID,loadExisting=False):
        self.projectID = projectID
        self.homeDir = os.path.join(self.baseDir,"projects",self.projectID)
        self.log.initialize(self.projectID,self.homeDir,load=loadExisting) 
        self.model.initialize(self.projectID,self.homeDir)

    ##################################################################################################
    #
    # data dealings -- handling file, project, model and figure data
    #
    ##################################################################################################
           
    def create_new_project(self,view=None,projectID=None):
        #fcsFileName = str(fcsFileName)
        createNew = True
    
        ## create projects dir if necssary
        if os.path.isdir(os.path.join(self.baseDir,'projects')) == False:
            print "INFO: projects dir did not exist. creating..."
            os.mkdir(os.path.join(self.baseDir,'projects'))

        ## get project id
        if projectID != None:
            pass
        elif createNew == True and projectID == None:
            projectID, ok = QtGui.QInputDialog.getText(view, self.appName, 'Enter the name of your new project:')
            projectID = str(projectID)
            
            if ok == False:
                createNew = False
        else:
            createNew = False
            print "ERROR: creating a new project"

        if createNew == True:
            print 'initializing project...'
            self.initialize_project(projectID)
        else:
            print "WARNING: did not initialize project"
            return False

        # remove previous 
        if self.homeDir != None and os.path.exists(self.homeDir) == True and createNew == True:
            print 'overwriting...', self.homeDir
            self.remove_project(self.homeDir)

        if createNew == True and self.homeDir != None:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            os.mkdir(os.path.join(self.homeDir,"figs"))
            os.mkdir(os.path.join(self.homeDir,"models"))
            os.mkdir(os.path.join(self.homeDir,"results"))

        return True

    def remove_project(self,homeDir):        
        for fileOrDir in os.listdir(homeDir):
            if os.path.isfile(os.path.join(homeDir,fileOrDir)) == True:
                os.remove(os.path.join(homeDir,fileOrDir))
            elif os.path.isdir(os.path.join(homeDir,fileOrDir)) == True:
                for fileOrDir2 in os.listdir(os.path.join(homeDir,fileOrDir)):
                    if os.path.isfile(os.path.join(homeDir,fileOrDir,fileOrDir2)) == True:
                        os.remove(os.path.join(homeDir,fileOrDir,fileOrDir2))
                    elif os.path.isdir(os.path.join(homeDir,fileOrDir,fileOrDir2)) == True:
                        for fileOrDir3 in os.listdir(os.path.join(homeDir,fileOrDir,fileOrDir2)):
                            if os.path.isfile(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3)) == True:
                                os.remove(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3))
                            elif os.path.isdir(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3)) == True:     
                                for fileName in os.listdir(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3)):
                                    os.remove(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3,fileName))
                                os.rmdir(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3))
                        os.rmdir(os.path.join(homeDir,fileOrDir,fileOrDir2))
                os.rmdir(os.path.join(homeDir,fileOrDir))
        os.rmdir(homeDir)

    def rm_file(self,fileName):
        if os.path.isfile(fileName) == False:
            print "ERROR: could not rm file: %s"%fileName
        else:
            os.remove(fileName)
            self.view.status.set("file removed")

    def load_fcs_files(self,fileList,dataType='fcs',transform='log'):
        if type(fileList) != type([]):
            print "INPUT ERROR: load_fcs_files: takes as input a list of file paths"

        script = os.path.join(self.baseDir,"LoadFile.py")
        self.log.log['transform'] = transform

        for filePath in fileList:
            proc = subprocess.Popen("%s %s -f %s -h %s -d %s -t %s"%(pythonPath,script,filePath,self.homeDir,dataType,transform),
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
            while True:
                try:
                    next_line = proc.stdout.readline()
                    if next_line == '' and proc.poll() != None:
                        break

                    ## to debug uncomment the following line     
                    print next_line

                except:
                    break

            ## check to see that files were made
            newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
            newFileName = re.sub('\.fcs|\.txt|\.out','',newFileName)
            newDataFileName = newFileName +"_data_original.pickle"
            newChanFileName = newFileName +"_channels_original.pickle"
            newFileName = re.sub('\s+','_',filePath[-1])
            if filePath == fileList[0]:
                self.log.log['selectedFile'] = re.sub("\.pickle","",newDataFileName)

            if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
                print "ERROR: data file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)
            if os.path.isfile(os.path.join(self.homeDir,'data',newChanFileName)) == False:
                print "ERROR: channel file was not successfully created", os.path.join(self.homeDir,'data',newChanFileName)

    #def load_additional_fcs_files(self,fileName=None,view=None):
    #    loadFile = True
    #    fcsFileName = None
    #    if fileName == None:
    #        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open FCS file')
    #
    #    if not re.search('\.fcs',fileName):
    #        fcsFileName = None
    #        view.display_warning("File '%s' was not of type *.fcs"%fileName)
    #    else:
    #        fcsFileName = fileName
    #
    #    if fcsFileName != None:
    #        self.load_fcs_file(fcsFileName)
    #        return True
    #    else:
    #        print "WARNING: bad attempt to load file name"
    #        return False

    def get_component_states(self):
        try:
            return self.view.resultsNavigationLeft.get_component_states()
        except:
            return None

    ##################################################################################################
    #
    # log files
    #
    ##################################################################################################

    def run_selected_model(self,progressBar=None,view=None):
        numItersMCMC = 1100
        selectedModel = self.log.log['modelToRun']
        numComponents = self.log.log['numComponents']
        

        if self.subsampleIndices == None:
            fileList = get_fcs_file_names(self.homeDir)
        elif self.subsampleIndices != None:
            fileList = get_fcs_file_names(self.homeDir,getPickles=True)

        percentDone = 0
        totalIters = float(len(fileList)) * numItersMCMC
        percentagesReported = []
        for fileName in fileList:

            if selectedModel == 'dpmm':
                script = os.path.join(self.baseDir,"RunDPMM.py")
                if os.path.isfile(script) == False:
                    print "ERROR: Invalid model run file path ", script 
                proc = subprocess.Popen("%s %s -h %s -f %s -k %s"%(pythonPath,script,self.homeDir,fileName,numComponents), 
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
                while True:
                    try:
                        next_line = proc.stdout.readline()
                        if next_line == '' and proc.poll() != None:
                            break
                       
                        ## to debug uncomment the following 2 lines
                        if not re.search("it =",next_line):
                            print next_line

                        if re.search("it =",next_line):
                            progress = 1.0 / totalIters
                            percentDone+=progress * 100.0
                            if progressBar != None:
                                progressBar.move_bar(int(round(percentDone)))
                            else:
                                if int(round(percentDone)) not in percentagesReported:
                                    percentagesReported.append(int(round(percentDone)))
                                    if int(round(percentDone)) != 100: 
                                        print "\r",int(round(percentDone)),"percent complete",
                                    else:
                                        print "\r",int(round(percentDone)),"percent complete"
                    except:
                        break
            else:
                print "ERROR: invalid selected model", selectedModel

                
