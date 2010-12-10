#!/usr/bin/env python

import os,re,cPickle
import fcm

def get_gene_list_names(homeDir,excludedFiles=[]):
    '''
    returns a sorted list of file names associated with the project
    
    '''

    if type(excludedFiles) != type([]):
        print "INPUT ERROR: bad type for excluded files in get_fcs_file_names"
        return None

    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"data")):
        if not re.search("\.pickle",fileName):
            continue

        if fileName not in excludedFiles:
            fileList.append(fileName)

    fileList = [re.sub("\_data.pickle","", fi) for fi in fileList]
    fileList.sort()

    return fileList


def get_project_names(baseDir):    
    '''
    returns all the projects on local computer
    
    '''
    if os.path.isdir(baseDir) == False:
        print "ERROR: bad base dir specified in get_project_names"

    projectNamesList = []
    projectDir = os.path.join(baseDir,"projects")
    if os.path.isdir(projectDir) == False:
        print "INFO: making project dir"
        os.mkdir(projectDir)

    for dirName in os.listdir(os.path.join(baseDir,"projects")):  
        if os.path.isdir(os.path.join(baseDir,"projects",dirName)) == True:
            if dirName not in ['utest','.svn']:
                projectNamesList.append(dirName)
    return projectNamesList


#def get_img_file_names(homeDir):
#    '''
#    return the file names for images 
#
#    '''
#
#    fileList = []
#    for fileName in os.listdir(os.path.join(homeDir,"figs")):
#        if re.search("\.png",fileName):
#            fileList.append(fileName)
#            
#    return fileList

#def get_models_run(homeDir, possibleModels):
#    '''
#    returns the models run
#    
#    '''
#    modelList = []
#    for fileName in os.listdir(os.path.join(homeDir,"models")):
#        # ignore classifications
#        if re.search("classify|\.log",fileName):
#            continue
#        
#        modelFound = None
#        for possibleModelUsed in possibleModels:
#            if modelFound != None:
#                continue
#
#            if re.search(possibleModelUsed,fileName):
#                modelList.append(re.sub("\_components\.pickle|\_modes\.pickle","",possibleModelUsed))
#        
#    modelList = list(set(modelList))
#
#    #if re.search("\.pickle",fileName):
#    #    modelList.append(fileName)
#
#    print "returning model list", modelList
#
#    return modelList


