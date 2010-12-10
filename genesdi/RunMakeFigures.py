#!/usr/bin/python
#
# to run an example
# python RunMakeFigures.py -p Demo -i 0 -j 1 -f 3FITC_4PE_004.fcs -h ./projects/Demo
#

import getopt,sys,os
import numpy as np

## important line to fix popup error in mac osx
import matplotlib
matplotlib.use('Agg')
from cytostream import Model
import matplotlib.pyplot as plt

## parse inputs
def bad_input():
    print "\nERROR: incorrect args"
    print sys.argv[0] + "-p projectID -i channel1 -j channel2 -f selectedFile -a alternateDirectory -s subset -t modelType -h homeDir"
    print "     projectID (-p) project name"
    print "     channel1 (-i) channel 1 name"
    print "      channel2 (-j) channel 2 name"
    print "      homeDir  (-h) home directory of current project"
    print "  selectedFile (-f) name of selected file"
    print "        altDir (-a) alternative directory (optional)"
    print "        subset (-s) subsampling number (optional)"
    print "     modelName (-m) model name"
    print "     modelType (-t) model type"
    print "\n"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:],'i:j:s:a:p:f:m:t:h:')
except getopt.GetoptError:
    print getopt.GetoptError
    bad_input()

projectID = None
channel1 = None
channel2 = None
selectedFile = None
altDir = None
homeDir = None
modelType = None
modelName = None
subset = "all"
run = True
for o, a in optlist:
    if o == '-i':
        channel1 = a
    if o == '-j':
        channel2 = a
    if o == '-f':
        selectedFile = a
    if o == '-a':
        altDir = a
    if o == '-p':
        projectID = a
    if o == '-s':
        subset = a
    if o == '-m':
        modelName = a
    if o == '-t':
        modelType = a
    if o == '-h':
        homeDir = a

def make_scatter_plot(model,selectedFile,channel1Ind,channel2Ind,subset='all',labels=None,buff=0.02,altDir=None):
    #fig = pyplot.figure(figsize=(7,7))
    markerSize = 5
    alphaVal = 0.5

    fontName = 'arial'
    fontSize = 12
    plotType = 'png'

    ## prepare figure
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)

    ## specify channels
    fileChannels = model.get_file_channel_list(selectedFile)
    index1 = int(channel1Ind)
    index2 = int(channel2Ind)
    
    channel1 = fileChannels[index1]
    channel2 = fileChannels[index2]
    data = model.pyfcm_load_fcs_file(selectedFile)
    
    ## subset give an numpy array of indices
    if subset != "all":
        subsampleIndices = model.get_subsample_indices(subset)
        data = data[subsampleIndices,:]

    ## make plot 
    totalPoints = 0
    if labels == None:
        ax.scatter([data[:,index1]],[data[:,index2]],color='blue',s=markerSize)
    else:
        if type(np.array([])) != type(labels):
            labels = np.array(labels)

        numLabels = np.unique(labels).size
        maxLabel = np.max(labels)
        cmp = model.get_n_color_colorbar(maxLabel+1)

        for l in np.sort(np.unique(labels)):
            rgbVal = tuple([val * 256 for val in cmp[l,:3]])
            hexColor = model.rgb_to_hex(rgbVal)[:7]

            x = data[:,index1][np.where(labels==l)[0]]
            y = data[:,index2][np.where(labels==l)[0]]
            
            totalPoints+=x.size

            if x.size == 0:
                continue
            ax.scatter(x,y,color=hexColor,s=markerSize)
            #ax.scatter(x,y,color=hexColor,s=markerSize)

    ## handle data edge buffers                                                                                                                                              
    bufferX = buff * (data[:,index1].max() - data[:,index1].min())
    bufferY = buff * (data[:,index2].max() - data[:,index2].min())
    ax.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
    ax.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])

    ## save file
    fileName = selectedFile
    ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)
    
    if altDir == None:
        fileName = os.path.join(model.homeDir,'figs',"%s_%s_%s.%s"%(selectedFile[:-4],channel1,channel2,plotType))
        fig.savefig(fileName,transparent=False,dpi=50)
    else:
        fileName = os.path.join(altDir,"%s_%s_%s.%s"%(selectedFile[:-4],channel1,channel2,plotType))
        fig.savefig(fileName,transparent=False,dpi=50)


## error checking
if altDir == 'None':
    altDir = None
if homeDir == 'None':
    homeDir = None
if modelName == 'None':
    modelName = None
    statModel,statModelClasses = None,None

if altDir == None and homeDir == None:
    bad_input()
    run = False
    print "WARNING: RunMakeFigures failed errorchecking"
 
if projectID == None or channel1 == None or channel2 == None or selectedFile == None:
    bad_input()
    run = False
    print "WARNING: RunMakeFigures failed errorchecking"

if os.path.isdir(homeDir) == False:
    print "ERROR: homedir does not exist -- bad project name", projectID, homeDir
    run = False

if altDir != None and os.path.isdir(altDir) == False:
    print "ERROR: specified alternative dir does not exist\n", altDir
    run = False

if run == True:
    model = Model()
    model.initialize(projectID,homeDir)

    if modelName == None:
        make_scatter_plot(model,selectedFile,channel1,channel2,subset=subset,altDir=altDir)
    else:
        statModel,statModelClasses = model.load_model_results_pickle(modelName,modelType) 
        make_scatter_plot(model,selectedFile,channel1,channel2,labels=statModelClasses,subset=subset,altDir=altDir)
