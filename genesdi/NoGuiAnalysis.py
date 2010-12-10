#!/usr/bin/env python

import sys,os,unittest,time,re
from PyQt4 import QtGui, QtCore
import subprocess

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg')

from cytostream import Controller, get_fcs_file_names
import numpy as np
BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class NoGuiAnalysis():
    def __init__(self,projectID,allFiles,subsample='1e4',makeQaFigs=True,makeResultsFigs=True, numComponents=16):
        ## error checking
        if type(allFiles) != type([]):
            print "ERROR:allFiles input must be of type list"
            return None

        self.projectID = projectID
        self.allFiles = allFiles
        self.subsample = subsample
        self.makeQaFigs = makeQaFigs
        self.makeResultsFigs = makeResultsFigs
        self.numComponents = numComponents
        self.initialize()

        for fileName in self.allFiles:
            self.controller.log.log['selectedFile'] = os.path.split(fileName)[-1]
            print 'running model on', self.controller.log.log['selectedFile']
            self.run_selected_model()

        ## create figures
        if self.makeResultsFigs == True:
            print 'creating results figures'
            self.controller.process_images('results')

    def initialize(self):
        self.controller = Controller()
        self.controller.initialize_project(self.projectID)
        
        firstFile = True
        goFlag = True
        for fileName in self.allFiles:

            if os.path.isfile(fileName) == False:
                print 'ERROR: Bad file name skipping', fileName
                continue

            print 'adding...', fileName
            fileName = str(fileName)
            if firstFile == True:
                self.controller.create_new_project(fileName)
                firstFile = False
            else:
                goFlag = self.controller.load_additional_fcs_files(fileName)

        if self.controller.homeDir == None:
            print "ERROR: project failed to initialize"
            return
        else:
            print "project created."
        
        # subsampling
        print "handling subsampling"
        self.controller.log.log['subsample'] = self.subsample
        self.controller.handle_subsampling()
        self.controller.save()
        
        # qa image creation
        if self.makeQaFigs == True:
            print 'making qa images'
            self.controller.process_images('qa')

    def run_selected_model(self):
        self.controller.log.log['numComponents'] = self.numComponents
        self.controller.log.log['modelToRun'] = 'dpmm'
        self.controller.run_selected_model()
        selectedFile = self.controller.log.log['selectedFile']
        modelName = "%s_sub%s_dpmm"%(re.sub("\.fcs|\.pickle","",selectedFile),int(float(self.subsample)))
        statModelModes, statModelClasses = self.controller.model.load_model_results_pickle(modelName,'modes')
        
### Run the tests 
if __name__ == '__main__':
    projectID = 'noguitest'
    allFiles = [os.path.join(BASEDIR,"example_data", "3FITC_4PE_004.fcs")]
    subsample = '1e4'
    nga = NoGuiAnalysis(projectID,allFiles,subsample)
