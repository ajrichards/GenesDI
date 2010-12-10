#!/usr/bin/env python
"""
The Model class is a interactive layer between gdi and outside packages like fcm.
It also handles reusable data manipulation functions, project initialization and other functions.
The class can be used alone

Adam Richards
adamricha@gmail.com
"""

try:
    from config_cs import configCS
    pythonPath = configCS['pythonPath']
except:
    pythonPath = 'python'

import sys,csv,os,re,cPickle,subprocess
sys.path.append("/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages")
import numpy as np
#from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names
from gdiqt4 import get_gene_list_names
from matplotlib import rc
import matplotlib.cm as cm
rc('font',family = 'sans-serif')
#rc('text', usetex = True)

class Model:
    """ 
    Class to carry out interfacing with data files and fcm library
    class is first created then initialized
        
    syntax:
        model = Model()
        model.initialize(projectID, homeDir)
    """

    def __init__(self):
        """
        Basic constructor method.  Class must be initialized before use. 

        """
        self.projectID = None
        self.homeDir = None

    def initialize(self,projectID,homeDir):
        """
        Associates a class with a project and home directory

        """
        self.projectID = projectID
        self.homeDir = homeDir

    def load_files(self,fileList,dataType='csv'):
        if type(fileList) != type([]):
            print "INPUT ERROR: load_files: takes as input a list of file paths"
            return None

        if os.path.isdir(self.homeDir) == False:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            print "INFO: making home dir from Model"


        script = os.path.join(self.homeDir,"..","..","LoadFile.py")


        for filePath in fileList:
            proc = subprocess.Popen("%s %s -f %s -h %s -d %s"%(pythonPath,script,filePath,self.homeDir,dataType),
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
            newFileName = re.sub('\.csv|\.txt','',newFileName)
            newDataFileName = newFileName +"_data.pickle"

            if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
                print "ERROR: data file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)

    def get_genes(self,fileName):
        """
        returns a np.array of gene symbols
        
        """
        
        fileName = fileName + "_data" + ".pickle"
        if os.path.isfile(os.path.join(self.homeDir,'data',fileName)) == False:
            print "INPUT ERROR: bad file name specified in model.get_genes"
            print "\t", os.path.join(self.homeDir,'data',fileName)
            return None
        
        tmp = open(os.path.join(self.homeDir,'data',fileName),'rb')
        geneList = cPickle.load(tmp)
        tmp.close()
        return geneList
        
    #def get_master_channel_list(self,excludedChannels=[]):
    #    """
    #    returns a unique, sorted set of channels for all files in a project
    #
    #    """
    # 
    #    allChannels = []
    #    fileList = get_fcs_file_names(self.homeDir)
    #    for fileName in fileList:
    #        fileChannels = self.get_file_channel_list(fileName,subsample='original')
    #
    #        allChannels+=fileChannels
    #    allChannels = np.sort(np.unique(allChannels))
    #
    #    ## remove white space
    #    allChannels = [re.sub("\s+","-",c) for c in allChannels]
    #
    #    return allChannels

    def load_model_results_pickle(self,modelName,modelType):
        """
        loads a pickled fcm file into the workspace
        data is a fcm data object
        k is the number of components
        the results are the last 5 samples from the posterior so here we average those samples then 
        use those data as a summary of the posterior
        """
        
        if modelType not in ['components','modes']:
            print "ERROR: invalide model type specified in load_model_results"
            return False

        tmp1 = open(os.path.join(self.homeDir,'models',modelName+"_%s.pickle"%modelType),'r')
        tmp2 = open(os.path.join(self.homeDir,'models',modelName+"_classify_%s.pickle"%modelType),'r')
        model = cPickle.load(tmp1)
        samplesFromPostr = 1.0
        k = int(model.pis().size / samplesFromPostr)
               
        classify = cPickle.load(tmp2)
        tmp1.close()
        tmp2.close()

        return model,classify
    
    def get_n_color_colorbar(self,n,cmapName='jet'):# Spectral #gist_rainbow
        "breaks any matplotlib cmap into n colors" 
        cmap = cm.get_cmap(cmapName,n) 
        return cmap(np.arange(n))

    def rgb_to_hex(self,rgb):
        """
        converts a rgb 3-tuple into hex
        """

        return '#%02x%02x%02x' % rgb[:3]
