#!/usr/bin/env python
'''
  MainWindow.py

  This program or module is free software: you can redistribute it and/or
  modify it under the terms of the GNU General Public License as published
  by the Free Software Foundation, either version 2 of the License, or
  version 3 of the License, or (at your option) any later version. It is
  provided for educational purposes and is distributed in the hope that
  it will be useful, but WITHOUT ANY WARRANTY; without even the implied
  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
  the GNU General Public License for more details.

  A. Richards
  adamricha@gmail.com

'''

import os,sys,time,re
import platform
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PyQt4.QtCore import  PYQT_VERSION_STR, QT_VERSION_STR
from PyQt4 import QtCore
from PyQt4 import QtGui

if hasattr(sys, 'frozen'):
    baseDir = os.path.dirname(sys.executable)
    baseDir = re.sub("MacOS","Resources",baseDir)
else:
    baseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(baseDir,'qtlib'))

#from OpenExistingProject import OpenExistingProject
from gdiqt4.qtlib import OpenExistingProject
from gdiqt4 import Controller
from gdiqt4.qtlib import BlankPage
from gdiqt4.qtlib import PipelineDock
from gdiqt4.qtlib import move_to_initial, move_to_data_processing, move_to_subset_finder, move_to_results_navigation
from gdiqt4.qtlib import create_menubar_toolbar
from LeftDock import *
from FileControls import *
#from StateTransitions import *

__version__ = "0.1"

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        
        ## construct and set main variables
        QtGui.QMainWindow.__init__(self)
       
        ## variables
        self.buff = 2.0
        self.controller = Controller()
        self.mainWidget = QtGui.QWidget(self)
        self.reset_view_workspace()
        self.stateList = ['Data Processing','Subset Finder','Results Navigation']
        ##self.possibleModels = ['dpmm']
        ##self.resultsModeList = ['modes','components']
        
        self.sizeLabel = QtGui.QLabel()
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.create_statusbar()
        create_menubar_toolbar(self)

        ## settings
        self.showMaximized()
        self.setWindowTitle(self.controller.appName)
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.screenWidth = screen.width()
        self.screenHeight = screen.height()
        self.eSize = 0.04 * self.screenWidth

        print 'moving to initial...'
        move_to_initial(self)


    #################################################
    #
    # variables and states
    #
    #################################################

    def reset_view_workspace(self):
        self.log = self.controller.log
        self.model = self.controller.model
        self.image = QtGui.QImage()
        self.dirty = False
        self.filename = None
        self.mainWidget = None
        self.dockWidget = None
        self.fileSelector = None
        self.pDock = None
        self.dock = None
        self.tv = None
        self.lastChanI = None
        self.lastChanJ = None

    #################################################
    #
    # forwarded functions
    #
    #################################################
    def add_left_dock(self):
        add_left_dock(self)

    def remove_left_dock(self):
        remove_left_dock(self)

    def move_to_initial(self,dummy=None):
        move_to_initial(self)

    def move_to_data_processing(self,dummy=None):
        move_to_data_processing(self)

    def move_to_subset_finder(self,dummy=None):
        move_to_subset_finder(self)

    def move_to_results_navigation(self,dummy=None):
        move_to_results_navigation(self)

    #################################################
    #
    # Statusbar
    #
    #################################################
    
    def create_statusbar(self):
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

    #################################################
    #
    # menubar and toolbar
    #
    #################################################
    
    def remove_project(self):
        projectID,projectInd = self.existingProjectOpener.get_selected_project()

        reply = QtGui.QMessageBox.question(self, self.controller.appName,
                                           "Are you sure you want to completely remove '%s'?"%projectID, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            homeDir = os.path.join(self.controller.baseDir,"projects",projectID)
            self.controller.remove_project(homeDir)
            self.open_existing_project()
        else:
            pass

    def create_new_project(self):
        self.controller.create_new_project(self)
       
        if self.controller.homeDir != None:
            self.pDock.set_btn_highlight('data processing')
            move_to_data_processing(self)
     
    def add_files_to_project(self):
        allFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open file(s)')
        allFilesList = [str(fileName) for fileName in allFiles]
        self.controller.model.load_files(allFilesList)
        move_to_data_processing(self)

    def open_existing_project(self):        
        if self.controller.projectID != None:
            reply = QtGui.QMessageBox.question(self, self.controller.appName,
                                               "Are you sure you want to close the current project - '%s'?"%self.controller.projectID, 
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return
            
        self.controller.reset_workspace()
        if self.dockWidget != None:
            remove_left_dock(self)

        closeBtnFn = lambda a=self: move_to_initial(a)
        self.mainWidget = QtGui.QWidget(self)
        projectList = get_project_names(self.controller.baseDir)
        self.existingProjectOpener = OpenExistingProject(projectList,parent=self.mainWidget,openBtnFn=self.open_existing_project_handler,
                                                         closeBtnFn=closeBtnFn,rmBtnFn=self.remove_project)
        hbl = QtGui.QHBoxLayout(self.mainWidget)
        hbl.setAlignment(QtCore.Qt.AlignTop)
        hbl.addWidget(self.existingProjectOpener)
        self.refresh_main_widget()

    def open_existing_project_handler(self):
        projectID,projectInd = self.existingProjectOpener.get_selected_project()
        self.controller.initialize_project(projectID,loadExisting=True)
        self.reset_view_workspace()
        self.refresh_state()
        #self.refresh_state()  # done twice to force correct visualation in pipeline
        
    def fileSave(self):
        if self.controller.homeDir != None:
            self.controller.save()
        else:
            self.display_warning("Must open project first before saving")

    def fileSaveAs(self):
        self.display_info("This function is not yet implimented")

    def filePrint(self):
        if self.image.isNull():
            return
        if self.printer is None:
            self.printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            self.printer.setPageSize(QtGui.QPrinter.Letter)
        form = QtGui.QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(),
                                size.height())
            painter.drawImage(0, 0, self.image)

    def show_image(self, percent=None):
        if self.image.isNull():
            return
        
        image = self.image
        self.pngViewer.setPixmap(QtGui.QPixmap.fromImage(image))

    def helpAbout(self):
        QtGui.QMessageBox.about(self, "About %s"%self.controller.appName,
                """<b>%s</b> v %s
                <p>Copyright &copy; 2010 Duke University. 
                All rights reserved.
                <p>This application can be used to perform
                model based analysis of flow cytometry data.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (self.controller.appName,
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def show_model_log_info(self):
        self.set_selected_model()

        selectedModel, selectedModelIndex = self.fileSelector.get_selected_model()
        fullModelName = re.sub("\.fcs|\.pickle","",self.log.log['selectedFile']) + "_" + selectedModel

        modelLogFile = self.log.read_model_log('%s_sub%s_%s'%(re.sub("\.fcs|\.pickle","",self.log.log['selectedFile']),
                                                              int(float(self.log.log['subsample'])),self.log.log['selectedModel'])) 
        QtGui.QMessageBox.about(self, "%s - Model Information"%self.controller.appName,
                          """<br><b>Project ID</b> - %s
                             <br><b>Model name</b> - %s
                             <br><b>Date time</b>  - %s
                             <br><b>Full  name</b> - %s
                             <br><b>File name</b>  - %s 
                             <br><b>Components</b> - %s
                             <br><b>Modes</b>      - %s
                             <br><b>Run time</b>   - %s"""%(modelLogFile['project id'],selectedModel,modelLogFile['timestamp'],
                                                     modelLogFile['full model name'],modelLogFile['file name'],
                                                     modelLogFile['number components'], modelLogFile['number modes'],modelLogFile['model runtime'])
                          )
    def helpHelp(self):
        self.display_info("The help is not yet implimented")
        #form = helpform.HelpForm("index.html", self)
        #form.show()

    ################################################################################################3

    def move_transition(self):
        bp = BlankPage(parent=self.mainWidget)
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(bp)
        vbl.addLayout(hbl)
        self.mainWidget.setLayout(vbl)
        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()
        
    def generic_callback(self):
        print "this button/widget does not do anything yet"


    #################################################
    #
    # Setters and handlers
    #
    #################################################

    def set_checks_array(self):
        if self.log.log['currentState'] == "Data Processing":
            checksArray = self.dpc.get_selected_channels()
            if type(checksArray) != type(np.array([])):
                print "ERROR in set_checks_array"
                return False
                                         
            self.log.log['checksArray'] = checksArray

            if self.log.log['checksArray'].sum() == 0:
                return True

            self.set_excluded_files_channels()

        return True  

    #def set_excluded_files_channels(self):
    #    if type(self.log.log['checksArray']) != type(np.array([])):
    #        print "ERROR cannot set excluded files or channels bad checksArray"
    #
    #    excludedFiles = []
    #    excludedChannels = []
    #    masterChannelList = self.model.get_master_channel_list()
    #    fileList = get_fcs_file_names(self.controller.homeDir)
    #    sumCols = self.log.log['checksArray'].sum(axis=0)
    #    sumRows = self.log.log['checksArray'].sum(axis=1)
    #    excludedChannels =  np.array(masterChannelList)[[int(i) for i in np.where(sumCols == 0)[0]]]
    #    excludedFiles =  np.array(fileList)[[int(i) for i in np.where(sumRows == 0)[0]]]
    #
    #    self.log.log['excludedChannels'] = excludedChannels.tolist()
    #    self.log.log['excludedFiles'] = excludedFiles.tolist()
    #    
    #    if self.controller.verbose == True:
    #        print 'setting excluding channels', excludedChannels
    #        print 'setting excluding files', excludedFiles 
    #
    #    ## adjust the selected file
    #    fileList = get_fcs_file_names(self.controller.homeDir)
    #    if type(self.log.log['excludedFiles']) == type([]) and len(self.log.log['excludedFiles']) > 0:
    #        for f in self.log.log['excludedFiles']:
    #            fileList.remove(f)
    #        self.log.log['selectedFile'] == fileList[0]

    #def set_num_components(self,value):
    #    diff = value % 8
    #    #print value, diff
    #    if diff == 0:
    #        newValue = value
    #    elif (value - diff) % 8 == 0:
    #        newValue = value - diff
    #    elif (value + diff) % 8 == 0:
    #        newValue = value + diff
    #
    #    self.log.log['numComponents'] = newValue

    def set_model_to_run(self):
        sm, smInd = self.dock.get_model_to_run()
        if sm == 'DPMM':
            self.log.log['modelToRun'] = 'dpmm'
        elif sm == 'K-means':
            self.log.log['modelToRun'] = 'kmeans'
        else:
            print "ERROR: invalid selection for modelToRun"

    def track_highest_state(self):
        ## keep track of the highest state
        if self.stateList.__contains__(self.log.log['currentState']):
            if self.stateList.index(self.log.log['currentState']) > self.log.log['highestState']:
                self.log.log['highestState'] = self.stateList.index(self.log.log['currentState'])

    def run_progress_bar(self):
        mode = self.log.log['currentState']

        self.set_widgets_enabled(False)

        if self.controller.subsampleIndices == None:
            self.controller.handle_subsampling()

        fileList = get_fcs_file_names(self.controller.homeDir)
        if mode == 'Quality Assurance':
            self.controller.process_images('qa',progressBar=self.progressBar,view=self)
            self.display_thumbnails()
        if mode == 'Model':
            self.set_model_to_run()
            self.controller.run_selected_model(progressBar=self.mc.progressBar,view=self)
            remove_left_dock(self)
            self.mainWidget = QtGui.QWidget(self)
            self.progressBar = ProgressBar(parent=self.mainWidget,buttonLabel="Create the figures")
            self.progressBar.set_callback(self.create_results_thumbs)
            hbl = QtGui.QHBoxLayout(self.mainWidget)
            hbl.addWidget(self.progressBar)
            hbl.setAlignment(QtCore.Qt.AlignCenter)
            self.refresh_main_widget()
            self.add_left_dock()

        self.set_widgets_enabled(True)

    def create_results_thumbs(self):
        self.controller.process_images('results',progressBar=self.progressBar,view=self)
        move_to_results_navigation(self,runNew=True)
 
    def display_thumbnails(self,runNew=False):
        mode = self.log.log['currentState']
        hbl = QtGui.QHBoxLayout()
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        
        ## adjust the selected file
        fileList = get_fcs_file_names(self.controller.homeDir)
        if type(self.log.log['excludedFiles']) == type([]) and len(self.log.log['excludedFiles']) > 0:
            for f in self.log.log['excludedFiles']:
                fileList.remove(f)
                
            self.log.log['selectedFile'] == fileList[0]

        if mode == 'Quality Assurance':
            self.mainWidget = QtGui.QWidget(self)
            imgDir = os.path.join(self.controller.homeDir,"figs")
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile']) 
            thumbDir = os.path.join(imgDir,self.log.log['selectedFile'][:-4]+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,viewScatterFn=self.handle_show_scatter)
            
        elif mode == 'Results Navigation':
            ## error checking
            modelsRun = get_models_run(self.controller.homeDir,self.possibleModels)
            if len(modelsRun) == 0:
                self.display_info("No models have been run yet -- so results cannot be viewed")
                return False

            self.log.log['selectedModel'] = modelsRun[0] 

            if self.log.log['selectedModel'] not in modelsRun:
                print "ERROR selected model not in models run"

            ## thumbs viewer
            self.mainWidget = QtGui.QWidget(self)
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile']) 

            if self.log.log['subsample'] == 'original':
                imgDir = os.path.join(self.controller.homeDir,'figs',self.log.log['selectedModel'])
            else:
                subset = str(int(float(self.log.log['subsample'])))
                imgDir = os.path.join(self.controller.homeDir,'figs',"sub%s_%s"%(subset,self.log.log['selectedModel']))
            
            if os.path.isdir(imgDir) == False:
                print "ERROR: a bad imgDir has been specified", imgDir

            thumbDir = os.path.join(imgDir,self.log.log['selectedFile'][:-4]+"_thumbs")
            self.tv = ThumbnailViewer(self.mainWidget,thumbDir,fileChannels,viewScatterFn=self.handle_show_scatter)
        
        else:
            print "ERROR: bad mode specified in display thumbnails"

        ## for either mode
        hbl.addWidget(self.tv)
        vbl.addLayout(hbl)
        self.mainWidget.setLayout(vbl)
        self.refresh_main_widget()
        
        if self.dock != None:
            ## disable buttons
            self.dock.disable_all()

        QtCore.QCoreApplication.processEvents()
        return True

    def handle_data_processing_mode_callback(self,item=None):
        if item != None:
            self.log.log['dataProcessingAction'] = item
            if item not in ['channel select']: 
                self.display_info("This stage is in beta testing and is not yet suggested for general use")
            move_to_data_processing(self)

    def set_selected_results_mode(self):
        #selectedMode, selectedModeInd = self.dock.get_selected_results_mode() 
        selectedMode = self.dock.get_results_mode()
        self.log.log['resultsMode'] = selectedMode
        self.handle_show_scatter(img=None)

    def set_selected_file(self):
        selectedFile, selectedFileInd = self.fileSelector.get_selected_file() 
        self.log.log['selectedFile'] = selectedFile
        
    def set_selected_model(self):
        selectedModel, selectedModleInd = self.fileSelector.get_selected_model()
        self.log.log['selectedModel'] = selectedModel

    def refresh_state(self):
        if self.log.log['currentState'] == "Data Processing":
            move_to_data_processing(self)
        elif self.log.log['currentState'] == "Quality Assurance":
            move_to_quality_assurance(self)
        elif self.log.log['currentState'] == "Model":
            move_to_model(self)
        elif self.log.log['currentState'] == "Results Navigation":
            move_to_results_navigation(self)
        elif self.log.log['currentState'] == "Results Summary":
            move_to_results_summary(self)

        QtCore.QCoreApplication.processEvents()

    def handle_show_scatter(self,img=None):
        mode = self.log.log['currentState']
        self.set_selected_file()
        
        ## layout and widget setup
        self.mainWidget = QtGui.QWidget(self)
        bp = BlankPage(parent=self.mainWidget)
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(bp)
        vbl.addLayout(hbl)
        self.mainWidget.setLayout(vbl)
        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()

        if img != None:
            channels = re.sub("%s\_|\_thumb.png"%re.sub("\.fcs","",self.log.log['selectedFile']),"",img)
            channels = re.split("\_",channels)
            chanI = channels[-2]
            chanJ = channels[-1]
            self.lastChanI = chanI
            self.lastChanJ = chanJ
            
        if self.lastChanI == None or self.lastChanJ == None:
            print "ERROR: lastChanI or lastChanJ not defined"
            return False

        if mode == "Quality Assurance":
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)
            sp = ScatterPlotter(self.controller.homeDir,self.log.log['selectedFile'],self.lastChanI,self.lastChanJ,
                                parent=self.mainWidget,subset=self.log.log['subsample'])
            ntb = NavigationToolbar(sp, self.mainWidget)
            vbl.addWidget(sp)
            vbl.addWidget(ntb)
        elif mode == "Results Navigation":
            self.set_selected_model()
            self.mainWidget = QtGui.QWidget(self)
            vbl = QtGui.QVBoxLayout(self.mainWidget)

            if self.log.log['subsample'] == 'original':
                modelName = re.sub("\.pickle|\.fcs","",self.log.log['selectedFile']) + "_" + self.log.log['selectedModel']
            else:
                subset = str(int(float(self.log.log['subsample'])))
                modelName = re.sub("\.pickle|\.fcs","",self.log.log['selectedFile']) + "_" + "sub%s_%s"%(subset,self.log.log['selectedModel'])

            sp = ScatterPlotter(self.controller.homeDir,self.log.log['selectedFile'],self.lastChanI,self.lastChanJ,subset=self.log.log['subsample'],
                                modelName=modelName,modelType=self.log.log['resultsMode'],parent=self.mainWidget)
            ntb = NavigationToolbar(sp, self.mainWidget)
            vbl.addWidget(sp)
            vbl.addWidget(ntb)
        
            ## enable buttons
            self.dock.enable_all()

        self.refresh_main_widget()
        QtCore.QCoreApplication.processEvents()

    def display_info(self,msg):
        '''
        display info
        generic function to display info to user
        '''
        reply = QtGui.QMessageBox.information(self, 'Information',msg)

    def display_warning(self,msg):
        '''
        display warning
        generic function to display a warning to user
        '''
        reply = QtGui.QMessageBox.warning(self, "Warning", msg)


    def refresh_main_widget(self):
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.activateWindow()
        self.mainWidget.update()
        self.show()
        #QtCore.QCoreApplication.processEvents()

    def set_widgets_enabled(self,flag):
        if flag not in [True, False]:
            print "ERROR: invalid flag sent to widgets_enable_all"
            return None

        if self.log.log['currentState'] == 'Data Processing':
            self.dock1.setEnabled(flag)
            self.dock2.setEnabled(flag)
            self.fileSelector.setEnabled(flag)
            self.pDock.setEnabled(flag)
        elif self.log.log['currentState'] == 'Quality Assurance':
            self.dock.setEnabled(flag)
            self.fileSelector.setEnabled(flag)
            self.pDock.setEnabled(flag)
       
