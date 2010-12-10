#!/usr/bin/python

'''
Cytostream
LeftDock        
Adam Richards
adamricha@gmail.com
                   
'''

import sys,os
from PyQt4 import QtGui,QtCore

if hasattr(sys,'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)

sys.path.append(os.path.join(baseDir,'..'))

#from FileControls import *
from gdiqt4 import get_gene_list_names
from gdiqt4.qtlib import GeneListSelector
from gdiqt4.qtlib.InitialDock1 import InitialDock1
from gdiqt4.qtlib import PipelineDock

def add_pipeline_dock(mainWindow):
    btnCallBacks = [lambda a=mainWindow:mainWindow.move_to_data_processing(a),
                    lambda a=mainWindow:mainWindow.move_to_subset_finder(a),
                    lambda a=mainWindow:mainWindow.move_to_results_navigation(a)]
   
    mainWindow.pDock = PipelineDock(parent=mainWindow.mainDockWidget,eSize=mainWindow.eSize,btnCallBacks=btnCallBacks)
    
def remove_left_dock(mainWindow):
    mainWindow.removeDockWidget(mainWindow.mainDockWidget)

def add_left_dock(mainWindow):
    if mainWindow.dockWidget != None:
        remove_left_dock(mainWindow)

    if mainWindow.controller.homeDir == None:
        noProject = True
        mainWindow.mainDockWidget = QtGui.QDockWidget('no project loaded', mainWindow)
    else:
        noProject = False
        allGeneLists = get_gene_list_names(mainWindow.controller.homeDir)
        mainWindow.mainDockWidget = QtGui.QDockWidget(mainWindow.controller.projectID, mainWindow)
    
    mainWindow.mainDockWidget.setObjectName("MainDockWidget")
    mainWindow.mainDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
    
    mainWindow.dockWidget = QtGui.QWidget(mainWindow)
    palette = mainWindow.dockWidget.palette()
    role = mainWindow.dockWidget.backgroundRole()
    palette.setColor(role, QtGui.QColor('black'))
    mainWindow.dockWidget.setPalette(palette)
    mainWindow.dockWidget.setAutoFillBackground(True)
    
    # setup alignments
    masterBox = QtGui.QVBoxLayout(mainWindow.dockWidget)
    vbox1 = QtGui.QVBoxLayout()
    vbox1.setAlignment(QtCore.Qt.AlignTop)
    hbox1 = QtGui.QHBoxLayout()
    hbox1.setAlignment(QtCore.Qt.AlignCenter)
    vbox2 = QtGui.QVBoxLayout()
    vbox2.setAlignment(QtCore.Qt.AlignBottom)
    hbox2 = QtGui.QHBoxLayout()
    hbox2.setAlignment(QtCore.Qt.AlignCenter)
    
    widgetWidth = 0.15 * mainWindow.screenWidth
    mainWindow.dockWidget.setMaximumWidth(widgetWidth)
    mainWindow.dockWidget.setMinimumWidth(widgetWidth)

    if mainWindow.log.log['currentState'] == 'initial':
        mainWindow.dock1 = InitialDock1(contBtnFn=False,addBtnFn=False,speciesFn=False,message="To begin select 'file' \nand create/load a project")
        mainWindow.dock1.setAutoFillBackground(True)
        hbox1.addWidget(mainWindow.dock1)
    elif mainWindow.log.log['currentState'] == 'Data Processing':
        mainWindow.dock1 = InitialDock1(contBtnFn=False,addBtnFn=mainWindow.add_files_to_project)
        mainWindow.dock1.setAutoFillBackground(True)
        hbox1.addWidget(mainWindow.dock1)
    
    ## add the pipeline dock
    add_pipeline_dock(mainWindow)
    hbox2.addWidget(mainWindow.pDock)
    ## finalize alignments
    vbox1.addLayout(hbox1)
    vbox2.addLayout(hbox2)
    masterBox.addLayout(vbox1)
    masterBox.addLayout(vbox2)
    #vbox.addLayout(vbl3)

    mainWindow.mainDockWidget.setWidget(mainWindow.dockWidget)
    mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mainWindow.mainDockWidget)

    ## file selector
    
    '''
    if mainWindow.log.log['currentState'] in ['Data Processing','Quality Assurance','Model','Results Navigation']:
        mainWindow.fileSelector = GeneListSelector(fileList,parent=mainWindow.dockWidget,
                                               selectionFn=mainWindow.set_selected_file,
                                               fileDefault=mainWindow.log.log['selectedFile'],
                                               showModelSelector=showModelSelector,modelsRun=modelsRun)
        mainWindow.fileSelector.setAutoFillBackground(True)
        subsamplingDefault = mainWindow.log.log['subsample']
        vbl1.addWidget(mainWindow.fileSelector)
     
    ## data processing
    if mainWindow.log.log['currentState'] == "Data Processing":
        mainWindow.dock1 = DataProcessingDock1(masterChannelList,transformList,compensationList,subsetList,parent=mainWindow.dockWidget,
                                              contBtnFn=None,subsetDefault=subsamplingDefault)
        callBackfn = mainWindow.handle_data_processing_mode_callback
        mainWindow.dock2 = DataProcessingDock2(callBackfn,parent=mainWindow.dockWidget,default=mainWindow.log.log['dataProcessingAction'])
        mainWindow.dock1.setAutoFillBackground(True)
        mainWindow.dock2.setAutoFillBackground(True)
        hbl2.addWidget(mainWindow.dock2)
        hbl3.addWidget(mainWindow.dock1)

    ## quality assurance
    elif mainWindow.log.log['currentState'] == "Quality Assurance":
        
        ### check to see if fileList needs adjusting
        #if type(mainWindow.log.log['excludedFiles']) == type([]) and len(mainWindow.log.log['excludedFiles']) > 0:
        #    for f in mainWindow.log.log['excludedFiles']:
        #        fileList.remove(f)
        #        print 'removeing file %s in leftdock'%f

        mainWindow.dock = QualityAssuranceDock(fileList,masterChannelList,transformList,compensationList,subsetList,parent=mainWindow.dockWidget,
                                               contBtnFn=None,subsetDefault=subsamplingDefault,viewAllFn=mainWindow.display_thumbnails)
        vbl3.addWidget(mainWindow.dock)
        mainWindow.dock.setAutoFillBackground(True)
   
    ## model
    elif mainWindow.log.log['currentState'] == "Model":
        modelList = ['DPMM','K-means']
        mainWindow.dock = ModelDock(modelList,parent=mainWindow.dockWidget,componentsFn=mainWindow.set_num_components)
        mainWindow.dock.setAutoFillBackground(True)
        vbl3.addWidget(mainWindow.dock)

    ## results navigation
    elif mainWindow.log.log['currentState'] == "Results Navigation":
        mainWindow.dock = ResultsNavigationDock(mainWindow.resultsModeList,masterChannelList,parent=mainWindow.dockWidget,
                                                resultsModeFn=mainWindow.set_selected_results_mode,
                                                resultsModeDefault=mainWindow.log.log['resultsMode'],viewAllFn=mainWindow.display_thumbnails,
                                                infoBtnFn=mainWindow.show_model_log_info)
        mainWindow.dock.setAutoFillBackground(True)
        vbl3.addWidget(mainWindow.dock)

    ## one dimensional viewer
    if mainWindow.log.log['currentState'] == 'OneDimViewer':
        mainWindow.dock = OneDimViewerDock(fileList,masterChannelList,callBack=mainWindow.odv.paint)
        mainWindow.dock.setAutoFillBackground(True)
        vbl1.addWidget(mainWindow.dock)
       
    ## stages with thumbnails
    if mainWindow.log.log['currentState'] in ['Quality Assurance', 'Results Navigation']:
        mainWindow.fileSelector.set_refresh_thumbs_fn(mainWindow.display_thumbnails)
    '''
   
