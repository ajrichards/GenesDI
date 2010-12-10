'''
A. Richards
'''

import os,re,sys,time
sys.path.append(os.path.join(".","MyWidgets"))
#from PIL import Image
from ImageTk import PhotoImage
import Tkinter as tk
import tkMessageBox
from tkFileDialog import askopenfilename
import numpy as np
from FileControls import *
from BuildingBlocks import *
from DataProcessingSettings import DataProcessingSettings
from QualityAssuranceSettings import QualityAssuranceSettings
from ModelSettings import ModelSettings
from ResultsNavigationSettings import ResultsNavigationSettings
from DataProcessingLeft import DataProcessingLeft
from ResolutionSelector import ResolutionSelector
from QualityAssuranceLeft import QualityAssuranceLeft
from ResultsNavigationLeft import ResultsNavigationLeft
from ExistingProjectsMenu import ExistingProjectsMenu
from ImageButtonMagic import ImageButtonMagic
from Statebar import Statebar


class View:
    def __init__(self,master,controller,model):
        self.master = master
        self.controller = controller
        self.log = self.controller.log
        self.model = model
        self.messageBoard = None
        self.centerAreaFrame = None
        self.leftAreaFrame = None
        self.dataProcessingSettings = None
        self.topAreaFrame = None
        self.stateBar = None
        self.stateList = ['Data Processing', 'Quality Assurance', 'Model', 'Results Navigation']
        self.bgcolor = self.master.cget("bg") #"#DDDDFF"  
        self.fgcolor = "#FFFF99" #"#CCCC66"
        self.lineNumber = 0
        
        # data processing variables 
        self.selectedTransform = 'option 1'
        self.selectedCompensation = 'option 1'
        self.subsampleStates = None

        # results navigation variables
        self.resultsMode = 'model select'
        self.selectedResultsChannel1 = None
        self.selectedResultsChannel2 = None
        self.selectedComponents = None

        ## change the window title (default is Tk) 
        self.master.wm_title(self.controller.appName)

        ## set area to screen size
        self.set_area_to_screen_size()
  
        ### create status bar
        self.status = StatusBar(self.master,self.controller)

        ### create the top area
        self.topArea = tk.Frame(self.master)
        self.topArea.pack(fill=tk.X,side=tk.TOP)
        self.topArea.config(bg=self.bgcolor)

        ### create frame pieces
        self.render_menus()
        self.render_rt_side()
        self.render_main_canvas()
        self.render_left_side()
      
    def set_area_to_screen_size(self):
        self.w,self.h = float(self.master.winfo_screenwidth()),float(self.master.winfo_screenheight())

        ## check for dual screens 
        if self.w > 2000:
            self.w = self.w / 2.0

        #self.controller.root.overrideredirect(1) # if you also want to get rid of the titlebar 
        self.master.geometry("%dx%d+0+0"%(self.w,self.h))
    
    def set_state(self,state,progressbarMsg=None,img=None,comparisonStates=None,resultsNavMode=None):
        self.log.log['currentState'] = state

        ## save project
        if self.controller.homeDir:
            self.log.write()
            print 'saving project at', self.log.log['currentState']

        ## keep track of the highest state
        if self.stateList.__contains__(self.log.log['currentState']):
            if self.stateList.index(self.log.log['currentState']) > self.log.log['highestState']:
                self.log.log['highestState'] = self.stateList.index(self.log.log['currentState'])
        
        if self.log.log['currentState'] == 'Progressbar':
            self.render_main_canvas(canvasState='progressbar',progressbarMsg=progressbarMsg)
        elif self.log.log['currentState'] == 'configuration':
            self.render_main_canvas(canvasState='configuration')     
        elif self.log.log['currentState'] == 'projects menu':
            self.render_main_canvas(canvasState='projects menu')
        elif self.log.log['currentState'] == 'initial':
            self.render_main_canvas(canvasState='initial')
        elif self.log.log['currentState'] == 'Data Processing':
            self.render_main_canvas(canvasState='processing')
        elif self.log.log['currentState'] == 'Quality Assurance':
            self.render_main_canvas(canvasState='qa',img=img,comparisonStates=comparisonStates)
        elif self.log.log['currentState'] == 'Model':
            self.render_main_canvas(canvasState='model')
        elif self.log.log['currentState'] == 'Results Navigation':
            self.render_main_canvas(canvasState='results',resultsNavMode=None)
        else:
            print "ERROR: invalid state specified: %s" %state
        
        self.render_state()
        
    ##############################################################################
    #
    # image manipulation functions
    #
    ##############################################################################

    def render_state(self):
        if self.stateBar != None:
            self.stateBar.destroy()
            
        self.stateBar = Statebar(self.topArea,self.stateList,self.log.log['currentState'],handleTransition=self.handle_state_transition)
        self.stateBar.config(bg=self.bgcolor)
        self.stateBar.pack(side=tk.TOP,fill=tk.X,pady=2,padx=5)

    def mount_image(self,fileName,recreate=True):
        if fileName != "experiment_icon":
            fileName = os.path.join(self.controller.homeDir,'figs',fileName)
            if os.path.isfile(fileName+".png") == False:
                print "ERROR: Bad specified image file name"
                self.i = PhotoImage(file = fileName + ".gif")
            else:
                self.i = PhotoImage(file = fileName + ".gif")
        else:
            self.i = PhotoImage(file = fileName + ".gif")

        imageX = 0.5*self.canvasWidth
        imageY = 0.45*self.canvasHeight
        self.canvas.delete("image")
        self.canvas.pack(fill=tk.BOTH,side=tk.TOP,anchor=tk.N)
        self.canvas.create_image(imageX,imageY,image=self.i,tags="image")
        self.canvas.config(bg=self.bgcolor)

    def unmount_image(self):
        self.canvas.delete(image)

    ##############################################################################
    #
    # menu functions
    #
    ##############################################################################

    def render_menus(self):
        ## initialize menu and menu commands as none
        self.filemenu = None
        self.helpmenu = None
        self.actionmenu = None

        ## load appropriate menus
        print 'loading menu'
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        
        ## file menu
        self.filemenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu = self.filemenu)
        
        self.filemenu.add_command(label="Create new project", command = self.create_new_project)
        self.filemenu.add_command(label="Open existing project", command = self.open_existing_projects_menu)
        self.filemenu.add_command(label="Export project", command = self.callback)
        self.filemenu.add_command(label="View project logfile", command = self.callback)

        if self.log.log['currentState'] in ['Quality Assurance','Model','Results Navigation']:
            self.filemenu.add_command(label="Export image", command = self.controller.saveas_image)
        
        self.filemenu.add_separator()
        if self.log.log['currentState'] in ['Data Processing','Quality Assurance','Model Preparation','Results Navigation']:
            self.filemenu.add_command(label="Close current project", command = self.topArea.quit)
        
        self.filemenu.add_command(label="Exit", command = self.topArea.quit)

        ## view menu
        self.viewmenu = tk.Menu(self.master)
        self.menu.add_cascade(label="View", menu=self.viewmenu)
        self.viewmenu.add_command(label="Set the default screen resolution", command=self.set_default_screen_resolution)
       
        ## action menu
        if self.log.log['currentState'] in ['Data Processing','Quality Assurance','Model','Results Navigation']:
            self.actionmenu = tk.Menu(self.menu)
            self.menu.add_cascade(label="Action", menu = self.actionmenu)
            self.actionmenu.add_command(label="action1", command = self.callback)

            if self.log.log['currentState'] in ['Data Processing']:
                self.actionmenu.add_command(label="Load additional file", command = self.controller.load_additional_fcs_files)

        ## help menu
        self.helpmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu = self.helpmenu)
        self.helpmenu.add_command(label="User Manual", command = self.controller.show_documentation)
        self.helpmenu.add_command(label="About...", command = self.callback)
    
    def render_rt_side(self):
        ### create the right side
        self.rightAreaFrame = tk.Frame(self.master)
        #self.rightAreaFrame.pack_propagate(0)
        self.rightAreaFrame["bg"] = self.bgcolor
        self.rightArea = tk.Canvas(self.rightAreaFrame, width = 0.02 * self.w, height = 0.95 * self.h)
        self.rightArea.configure(background = self.bgcolor)
        self.rightAreaFrame.pack(side = tk.RIGHT)
        self.rightArea.pack()

    ##############################################################################
    #
    # main canvas functions
    #
    ##############################################################################

    def open_existing_projects_menu(self):
        self.set_state('projects menu')

    def open_existing_project(self):
        selectedProject = self.existingProjectsMenu.get_selected_project()
        if selectedProject != None:
            self.controller.projectID = selectedProject
            self.controller.homeDir = os.path.join(".","projects",self.controller.projectID)
            self.log.initialize(self.controller.projectID,self.controller.homeDir,load=True)
            self.controller.handle_subsampling()
            self.set_state(self.log.log['currentState'])
            print "the current state: ", self.log.log['currentState']
        else:
            self.display_warning("You must select an existing project first")

    def render_main_canvas(self,canvasState='initial',progressbarMsg=None,img=None,comparisonStates=None,useCurrentStates=False,resultsNavMode=None):

        ### create the center
        if self.centerAreaFrame != None:
            self.centerAreaFrame.destroy()
            
        self.canvasWidth = 0.72 * self.w       # 0.72
        self.canvasHeight = 0.95 * self.h      # 0.85 remember to change them all
        self.controller.mainAreaWidth = self.canvasWidth
        self.controller.mainAreaHeight = self.canvasHeight
        self.textSpacing = 0.02* self.canvasHeight
        self.centerAreaFrame = tk.Frame(self.master,height=self.canvasHeight,width=self.canvasWidth)
        self.centerAreaFrame["bg"] = self.bgcolor
        self.centerAreaFrame.pack_propagate(0) # don't shrink
        self.centerAreaFrame.pack(side = tk.RIGHT)       
        self.canvas = tk.Canvas(self.centerAreaFrame,height=self.canvasHeight,width=self.canvasWidth)
        
        if canvasState != 'initial' and self.controller.homeDir != None:
            fileNames  = get_fcs_file_names(self.controller.homeDir)

        if canvasState == 'initial':
            self.mount_image("experiment_icon")
            print 'rendering main canvas -- initial'
            self.canvas.pack()
        elif canvasState == 'configuration':
            msg = "Your current screen geometry is %sx%s\nHere you may select another resolution\n\n"%(int(self.w), int(self.h))
            self.resolutionSelector = ResolutionSelector(self.centerAreaFrame,msg,bg=self.bgcolor,fg=self.fgcolor,command=self.change_default_screen_resolution)
        elif canvasState == 'progressbar':
            self.progressbar = Progressbar(self.centerAreaFrame,withLabel=progressbarMsg,bg=self.bgcolor,fg=self.fgcolor)
            self.progressbar.pack(side=tk.TOP,fill=tk.BOTH,pady=0.2*self.canvasHeight,anchor=tk.S)

        elif canvasState == 'processing':
            dataProcessing = True
            masterChannelList = self.model.get_master_channel_list()
            if useCurrentStates == False:
                self.set_selected_channel_states()
            self.dataProcessingSettings = DataProcessingSettings(self.centerAreaFrame,fileNames,masterChannelList,width=self.canvasWidth,
                                                                 bg=self.bgcolor,fg=self.fgcolor,showNameBtn=self.display_file_by_button,
                                                                 loadbtnFn=self.controller.load_additional_fcs_files,selectAllFn=self.handle_select_all_channels,
                                                                 channelStates=self.controller.log.log['processingChannels'],contbtnFn=self.processing_to_qa)
        elif canvasState == 'qa':
            imgNames = get_img_file_names(self.controller.homeDir)
            imgNames = [image[:-4] for image in imgNames]
            self.canvas = tk.Canvas(self.centerAreaFrame,height=self.canvasHeight,width=self.canvasWidth)

            if img != None:
                self.mount_image(img) # img
                self.canvas.pack(anchor=tk.N,side=tk.TOP)
            else:
                mode = 'view all'
                self.qualityAssuranceSettings = QualityAssuranceSettings(self.centerAreaFrame,mode,fileNames,imgNames,self.controller.homeDir,
                                                                         imgHandler = self.show_selected_image, width=self.canvasWidth,
                                                                         bg=self.bgcolor,fg=self.fgcolor,allStates=comparisonStates,
                                                                         contbtnFn=self.qa_to_model,selectAllCmd=None)
                self.qualityAssuranceSettings.pack()

        elif canvasState == 'model':
            self.modelSettings = ModelSettings(self.centerAreaFrame,fileNames,width=self.canvasWidth,
                                               bg=self.bgcolor,fg=self.fgcolor,runModelBtnFn=self.model_to_results_navigation,
                                               contbtnFn=self.model_to_results_navigation)
        elif canvasState == 'results':
            modelList = get_models_run(self.controller.homeDir)

            if self.resultsMode in ['model select']:
                self.resultsNavigationSettings = ResultsNavigationSettings(self.centerAreaFrame,modelList,self.resultsMode,width=self.canvasWidth,
                                                                           dblClickBtnFn=self.show_model_log,bg=self.bgcolor,fg=self.fgcolor,
                                                                           loadbtnFn=None,contBtnFn=self.handle_results_navigation_settings)
                self.resultsSelectCanvas = tk.Canvas(self.centerAreaFrame,width=0.5*self.canvasWidth,height=0.5*self.canvasHeight)
                self.resultsSelectCanvas.configure(background=self.bgcolor)
                self.resultsSelectCanvas.pack(side=tk.LEFT)

            else:

                if self.selectedResultsChannel1 == None or self.selectedResultsChannel2 == None:
                    fileName = self.log.log['selectedFile']
                    imgDir = os.path.join(self.controller.homeDir,'figs',re.sub(fileName[:-4]+"\_","",self.log.log['selectedModel']))
                    imageHandler = self.show_selected_image
                    self.ibm = ImageButtonMagic(self.centerAreaFrame,imgDir,imageHandler)
                    self.ibm.config(bg=self.bgcolor)
                    self.ibm.pack()
                else:
                    ### get model
                    if not self.statModel:
                        self.statModel,self.modelClasses = self.model.load_model_results_pickle(self.log.log['selectedModel'])
                    try: self.statModel
                    except:
                        self.statModel = None
                        self.statModelClasses = None

                    self.mplCanvas = self.model.make_scatter_plot(self.log.log['selectedFile'],self.selectedResultsChannel1,
                                                                  self.selectedResultsChannel2,labels=self.statModelClasses,
                                                                  root=self.centerAreaFrame,width=self.canvasWidth,height=self.canvasHeight,getCanvas=True)
                    self.mplCanvas._tkcanvas.pack(fill=tk.BOTH,expand=1)

        elif canvasState == 'projects menu':
            existingProjects = get_project_names()
            self.existingProjectsMenu = ExistingProjectsMenu(self.centerAreaFrame,existingProjects,bg=self.bgcolor,fg=self.fgcolor,
                                                             command=self.open_existing_project,loadBtnFn=self.open_existing_project)
            self.existingProjectsMenu.pack()

        ### finally render the left side    
        self.render_left_side()

    def display_file_by_button(self,ind):
        fileList = get_fcs_file_names(self.controller.homeDir)
        if ind == 0:
            self.status.set("Does that look like a file to you?")
        else:
            self.status.set(fileList[ind-1])

    def handle_select_all_channels(self):
        self.set_state("Data Processing")

    def set_selected_channel_states(self):

        masterList = self.model.get_master_channel_list()
        fileList = get_fcs_file_names(self.controller.homeDir)

        ## create a list of list to represent the channel states (each list is one row) 
        channelStates = [ [0]+np.zeros(len(masterList),dtype=int).tolist()+[0,0,0] for c in range(len(fileList))]

        ## if applicable get selected channels  
        if self.dataProcessingSettings != None:
            selectedChannels = self.dataProcessingSettings.get_selected_channels()
            for row in range(len(selectedChannels)):
                for col in range(len(selectedChannels[0])):
                    state = selectedChannels[row][col]
                    if state != 0:
                        channelStates[row][col] = state

        ## check to see if select all was used  
        selectedRow = None
        if self.dataProcessingSettings != None:
            currentChannels = self.log.log['processingChannels']

            for row in range(len(selectedChannels)):
                stateSelected = selectedChannels[row][0]
                stateCurrent = currentChannels[row][0]
            
                if stateSelected != stateCurrent:
                    selectedRow = row

            if selectedRow != None:
                if currentChannels[selectedRow][0] == 1:
                    channelStates[selectedRow] = [0 for i in range(len(currentChannels[row]))]
                elif currentChannels[selectedRow][0] == 0:
                    channelStates[selectedRow] = [1 for i in range(len(currentChannels[row]))]

        ## ready unavailable channels for disabling (-1)
        for f in range(len(fileList)):
            file = fileList[f]
            channels = self.model.get_file_channel_list(file)
            masterIndices = [np.where(np.array(masterList) == ch)[0][0] for ch in channels]
            disabledChannels = list(set(range(len(masterList))).difference(set(masterIndices)))
            for c in range(len(masterList)):
                if c in disabledChannels:
                    channelStates[f][c+1] = -1
        
        self.controller.log.log['processingChannels'] = channelStates

    ##############################################################################
    #
    # messageboard, fileselector
    #
    ##############################################################################

    def render_left_side(self,selectAllCompares=False):
        
        ### create the left side
        if self.leftAreaFrame != None:
            self.leftAreaFrame.destroy()
        
        self.leftAreaFrame = tk.Frame(self.master,height=self.canvasHeight)
        self.leftAreaFrame["bg"] = self.bgcolor
        self.leftAreaFrame.pack(side = tk.RIGHT,expand=tk.Y)

        ## to be carried out everytime the left are frame is rendered
        if self.controller.homeDir:
            fileList = get_fcs_file_names(self.controller.homeDir)
            imgNames = get_img_file_names(self.controller.homeDir) 
            if self.log.log['selectedFile'] == None:
                self.log.log['selectedFile'] = fileList[0]
                
            fileStates = [tk.NORMAL for i in fileList]
            fileStates[fileList.index(self.log.log['selectedFile'])] = tk.ACTIVE

        ## data processing
        if self.log.log['currentState'] == 'Data Processing':
            self.dataProcessingLeft = DataProcessingLeft(self.leftAreaFrame,fileList,fileStates,bg=self.bgcolor,fg=self.fgcolor,subsampleStates=self.subsampleStates,
                                                         selectedTransformCmd=self.set_selected_transform,subsampleFn=self.set_subsample,  
                                                         selectedCompCmd=self.set_selected_compensation,selectedCompensation=self.selectedCompensation,
                                                         selectedTransform = self.selectedTransform,uploadBtnFn=None,uploadFcsFn=self.controller.load_additional_fcs_files,
                                                         rmBtnFn=self.rm_selected_file,fileSelectorResponse=self.file_selector_response)
            self.dataProcessingLeft.pack(side=tk.TOP)

        ## quality assurance 
        elif self.log.log['currentState'] == 'Quality Assurance':
            self.qualityAssuranceLeft = QualityAssuranceLeft(self.leftAreaFrame,imgNames,fileList,fileStates,fileSelectorResponse=self.file_selector_response,
                                                             bg=self.bgcolor,fg=self.fgcolor,viewSelectedCmd=self.show_selected_image,  
                                                             contbtnFn=self.qa_to_model,returnBtnFn=self.close_image_viewer,viewAllFn=self.handle_view_all)
            self.qualityAssuranceLeft.pack(side=tk.TOP)
        
        ## results navigation
        elif self.log.log['currentState'] == 'Results Navigation':
            modelNames = get_models_run(self.controller.homeDir) 
            channelList = self.model.get_file_channel_list(self.log.log['selectedFile'])
            model = None

            # get file specific indices 
            try:
                self.statModel,self.statModelClasses = self.model.load_model_results_pickle(self.log.log['selectedModel'])
                channelsSelected = self.log.log['resultsChannels']
                fileSpecificIndices = [channelList.index(i) for i in channelsSelected]
            except:
                fileSpecificIndices = None
                self.statModel = None
                self.statModelClasses = None
                channelsSelected = None

            if self.log.log['componentStates'] != None:
                componentStates = self.log.log['componentStates']
            else:
                componentStates = None

            self.resultsNavigationLeft = ResultsNavigationLeft(self.leftAreaFrame,channelList,self.resultsMode,fileList,fileStates,self.statModel,
                                                               selectedInds = fileSpecificIndices,fileSelectorResponse=self.file_selector_response,
                                                               bg=self.bgcolor,fg=self.fgcolor,viewSelectedCmd=self.show_selected_image,
                                                               contbtnFn=self.qa_to_model,componentStates = componentStates,viewAllFn=self.handle_view_all,
                                                               returnBtnFn=self.close_image_viewer,rerenderFn=self.handle_results_navigation_figures)
            self.resultsNavigationLeft.pack(side=tk.TOP)

        self.messageBoard = tk.Canvas(self.leftAreaFrame,width=0.3*self.w,height=self.canvasHeight)
        self.messageBoard.configure(background = self.bgcolor)
        self.messageBoard.pack(side=tk.LEFT,expand=tk.Y)

    ## this function is called from the fileselector widget
    def file_selector_response(self):
        if self.log.log['currentState'] == "Data Processing":
            self.lineNumber = 0
            self.log.log['selectedFile'] = self.dataProcessingLeft.get_selected_file()
            file = self.model.pyfcm_load_fcs_file(self.log.log['selectedFile'])

            n,d = np.shape(file)
            self.render_left_side()
            self.message_board_display("file - %s "%self.log.log['selectedFile'])
            self.message_board_display("observations -  %s "%n)
            self.message_board_display("dimensions -  %s "%d)
        else:
            print "resonse method not available yet"

    #########################################################################
    # 
    # Results navigation handles
    #
    #########################################################################

    def handle_results_navigation_settings(self):
        selectedModel = self.resultsNavigationSettings.get_selected_model()
        fileList = get_fcs_file_names(self.controller.homeDir)
        fileName = None

        if selectedModel != None:
            for file in fileList:
                m = re.search(re.sub("[\.fcs|\.pickle]","",file),selectedModel)
                if m:
                    fileName = m.group(0)
        
        if selectedModel != None:
            self.log.log['selectedModel'] = selectedModel
            self.log.log['selectedFile'] = fileName + ".fcs"
            self.resultsMode = 'mixture components'
            self.set_state('Results Navigation')
        elif selectedModel == None:
            self.display_warning("You must select a model before navigating its results")

    def handle_results_navigation_figures(self):
        imageChannels = self.resultsNavigationLeft.get_image_channels()
        self.log.log['componentStates'] = self.resultsNavigationLeft.get_component_states()
        if not self.statModel:
            self.statModel,self.statModelClasses = self.model.load_model_results_pickle(self.log.log['selectedModel'])

        if imageChannels != None:
            self.selectedResultsChannel1 = imageChannels[0]
            self.selectedResultsChannel2 = imageChannels[1]
            self.log.log['resultsChannels'] = [imageChannels[0],imageChannels[1]]
            print "setting results channels to", self.log.log['resultsChannels']
            self.set_state('Results Navigation')
        else:
            self.display_warning("You must select a two channels file before viewing a plot")

    def handle_results_navigation_model_summary(self):
        print 'handling results naviation model summary'


    def show_model_log(self):
        selectedModel = self.resultsNavigationSettings.get_selected_model()
        fileList = get_fcs_file_names(self.controller.homeDir)
        fileName = None
        for file in fileList:
            m = re.search(re.sub("[\.fcs|\.pickle]","",file),selectedModel)
            if m:
                fileName = m.group(0)
        
        lineCount = 1
        whiteSpace = self.h / 70.0
        modelLogFile = self.log.read_model_log(selectedModel)
        self.resultsSelectCanvas.delete(tk.ALL)
        logKeys = modelLogFile.keys()
        logKeys.sort()

        for key in logKeys:
            item = modelLogFile[key]
            self.resultsSelectCanvas.create_text(0.05*self.w,lineCount*whiteSpace,text="%s - %s"%(key,item),fill="black",anchor=tk.W)
            lineCount+=1

        self.status.set("displaying results for %s"%selectedModel)

            
    #########################################################################
    # 
    #  Data processing handles
    #
    #########################################################################

    def rm_selected_file(self):
        
        if self.log.log['selectedFile'] == None:
            self.display_warning("You must select a file before removing it")
        else:
            selectedFile = os.path.join(self.controller.homeDir,'data',self.log.log['selectedFile'])
            self.controller.rm_fcs_file(selectedFile)
            self.log.log['selectedFile'] = None
            self.set_state("Data Processing")
    
    def set_selected_transform(self):
        self.selectedTransform = self.dataProcessingLeft.get_selected_transform()

    def set_selected_compensation(self):
        self.selectedCompensation = self.dataProcessingLeft.get_selected_compensation()

    def message_board_display(self,msg,align='left',withButton=False):
        if self.lineNumber == 0:
            self.render_left_side()

        whiteSpace = self.h / 100.0
        self.lineNumber+=1
        
        if self.lineNumber == 1:
            self.lineNumber+=1
            self.message_board_display("Project - %s"%self.controller.projectID,align='left')
            self.lineNumber+=1
            lineHeight = (self.lineNumber * whiteSpace) #+ (0.1 * whiteSpace)
            self.messageBoard.create_line((0,lineHeight),(0.3*self.w,lineHeight), fill="black")
            self.lineNumber+=2

        if align=='center':
            self.messageBoard.create_text(0.15*self.w,self.lineNumber*whiteSpace,text=msg,fill="black",tags="line"+str(self.lineNumber),anchor=tk.CENTER)
            self.lineNumber+=1
        elif align == 'left':
            self.messageBoard.create_text(0.008*self.w,self.lineNumber*whiteSpace,text=msg,fill="black",tags="line"+str(self.lineNumber),anchor=tk.W)
            self.lineNumber+=1
        else:
            print "ERROR: did not impliment other aligns besides center and left"

    def show_fcs_file_names(self):
        self.lineNumber = 0
        for fileName in os.listdir(os.path.join(self.controller.homeDir,"data")):
            if re.search("\.fcs",fileName):
                self.message_board_display("file - %s"%fileName,align='left', withButton=True)

    def show_selected_image(self):
        
        if self.log.log['currentState'] == 'Quality Assurance':
            img = self.qualityAssuranceLeft.get_selected_image()
        
            if img == None:
                img = self.qualityAssuranceSettings.ibm.selectedImg
                img = os.path.split(img)[-1]
                img = re.sub('\_thumb','',img)[:-4]

            self.set_state('Quality Assurance',img=img)

        elif self.log.log['currentState'] == 'Results Navigation':
            print 'should be handling generatino of image'
            fileChannels = self.model.get_file_channel_list(self.log.log['selectedFile'])

            img = self.ibm.selectedImg
            img = os.path.split(img)[-1]
            img = re.sub('\_thumb','',img)[:-4]

            # get the channels from file name
            imageChannels = []
            for chan in fileChannels:
                if re.search(chan,img):
                    imageChannels.append(chan)

            self.log.log['componentStates'] = self.resultsNavigationLeft.get_component_states()
            if not self.statModel:
                self.statModel,self.statModelClasses = self.model.load_model_results_pickle(self.log.log['selectedModel'])
            
            if imageChannels != None:
                self.selectedResultsChannel1 = imageChannels[0]
                self.selectedResultsChannel2 = imageChannels[1]
                self.log.log['resultsChannels'] = [imageChannels[0],imageChannels[1]]
                print "setting results channels to", self.log.log['resultsChannels']
                self.set_state('Results Navigation')

    def set_subsample(self):
        if self.dataProcessingLeft.get_subsample() != 'All Data':
            ss = re.sub("\s","",self.dataProcessingLeft.get_subsample())
        else:
            ss = self.dataProcessingLeft.get_subsample()
        self.log.log['subsample'] = ss
        subsamples = ['All Data','1e3','1e4','5e4']                 # make sure this matches in dataprocessingleft
        self.subsampleStates = [tk.NORMAL for st in range(len(subsamples))]
        if subsamples.__contains__(self.log.log['subsample']) == True:
            self.subsampleStates[subsamples.index(self.log.log['subsample'])] = tk.ACTIVE

    def create_new_project(self):
        tkMessageBox.showinfo(self.controller.appName,"Load a *.fcs file ")       
        fcsFileName = askopenfilename()  
        self.controller.create_new_project(fcsFileName)

        if self.controller.homeDir != None:
            self.set_state("Data Processing")

    #########################################################################
    # 
    #  Reuseable handles
    #
    #########################################################################

    def handle_view_all(self):
        if self.log.log['currentState'] == "Quality Assurance":
            self.set_state('Quality Assurance')

        if self.log.log['currentState'] == "Results Navigation":
            self.selectedResultsChannel1 = None
            self.selectedResultsChannel2 = None
            self.log.log['resultsChannels'] = None
            self.set_state('Results Navigation')

    def close_image_viewer(self):
        self.set_state(self.log.log['currentState'])

    def select_all_comparisons(self):
        if self.log.log['currentState'] == 'Quality Assurance':
            selectState = self.qualityAssuranceSettings.get_select_all_state()
        elif self.log.log['currentState'] == 'Results Navigation':
            selectState = self.resultsNavigationSettings.get_select_all_state()
        
        imgNames = get_img_file_names(self.controller.homeDir)
        imgNames = [image[:-4] for image in imgNames]
    
        if selectState[0] == 1:
            comparisonStates = [tk.ACTIVE for i in imgNames]
        else:
            comparisonStates = None
    
        self.set_state(self.log.log['currentState'],comparisonStates=comparisonStates)

    
    ##############################################################################
    #
    # model handles
    #
    ##############################################################################

    def run_selected_model(self):
        modelSelectedLong = self.modelSettings.get_selected_model()
        self.set_state('Progressbar',progressbarMsg="Running '%s'..."%modelSelectedLong)

        fileList = get_fcs_file_names(self.controller.homeDir)
        
        if modelSelectedLong == "Dirichlet Process Mixture Model - CPU Version":
            self.log.log['modelToRun'] = "dpmm-cpu"
        elif modelSelectedLong == "Dirichlet Process Mixture Model - GPU Version":
            self.log.log['modelToRun'] = "dpmm-gpu"
        elif modelSelectedLong == "Spectral Clustering - Ng Algorithm":
            self.log.log['modelToRun'] = "sc-ng"
        else:
            print "ERROR: run selected model returned a bad model name:%s"%modelSelectedLong

        self.controller.run_selected_model()
        self.status.set("Model run finished")

    ##############################################################################
    #
    # functions that control the state transitions
    #
    ##############################################################################

    def handle_state_transition(self):
        state = self.stateBar.get_current_state()

        #if self.stateList.__contains__(self.log.log['currentState']):
        if self.stateList.index(state) > self.log.log['highestState']:
            self.display_warning('User must follow the flow of the pipeline \n i.e. please do not skip steps')
            self.render_state()
        else:

            ## reset stage specific variables
            self.resultsMode = 'model select'
            self.selectedResultsChannel1 = None
            self.selectedResultsChannel2 = None
            self.selectedComponents = None

            self.set_state(state)


    def processing_to_qa(self):
        #self.set_selected_channel_states()
        #if np.array(selectedChannels).sum() < 2:
        #    self.display_error("you must select at least 2 channels")
        #else:
        self.set_state('Progressbar',progressbarMsg="Creating all specified images...")
        self.status.set("addressing subsampling...")
        self.set_subsample()
        self.controller.handle_subsampling()
        self.set_selected_channel_states()
        self.status.set("Rendering images...")
        self.controller.process_images()
        self.status.set("Assess the quality and return to previous steps if necessary")
        self.set_state('Quality Assurance')
            
    def qa_to_model(self):
        self.set_state('Model')

    def model_to_results_navigation(self):
        self.run_selected_model()
        self.set_state('Progressbar',progressbarMsg="Rendering images'...")
        self.controller.process_results_images(self.log.log['modelToRun'])
        self.set_state('Results Navigation')

    def enable_cluster_selection(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<ButtonPress-1>", self.model.press)
        self.canvas.bind("<ButtonRelease-1>", self.model.release)


    ##############################################################################
    #
    # basic message functions
    #
    ##############################################################################

    def display_info(self,message):
        tkMessageBox.showinfo(self.controller.appName, message)
        self.status.set("info: %s"%message)

    def display_warning(self,message):
        tkMessageBox.showwarning(self.controller.appName, message)
        self.status.set("warning: %s"%message)

    def display_error(self,message):
        tkMessageBox.showerror(self.controller.appName, message)
        self.status.set("error: %s"%message)

    def callback(self):
        tkMessageBox.showinfo(self.controller.appName, "this function does not exist yet")
        self.status.set("this function does not exist yet")


    ##############################################################################
    #
    # system specific functions
    #
    ##############################################################################

    def set_default_screen_resolution(self):
        self.set_state('configuration')

    def change_default_screen_resolution(self):
        newRes = self.resolutionSelector.get_selected_resolution()
        width,height = newRes.split('x')
        self.w = float(width)
        self.h = float(height)
        self.master.geometry("%dx%d+0+0"%(self.w,self.h))

        ### create the top area
        self.topArea.destroy()
        self.filemenu.destroy()
        self.leftAreaFrame.destroy()
        self.rightAreaFrame.destroy()
        self.centerAreaFrame.destroy()

        self.topArea = tk.Frame(self.master)
        self.topArea.pack(fill=tk.X,side=tk.TOP)
        self.topArea.config(bg=self.bgcolor)

        ### create frame pieces 
        self.render_menus()
        self.render_rt_side()
        self.render_main_canvas()
        self.render_left_side()

        self.status.destroy()
        self.status = StatusBar(self.master,self.controller)
        self.status.set('resolution has been set to %s'%newRes)

    
    ##############################################################################
    #
    # status bar class
    #
    ##############################################################################

class StatusBar(tk.Frame):
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.frame = tk.Frame.__init__(self, self.master)
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label.config(text = " Load an existing project or a new FCS file to get started ")
        self.label.pack(fill=tk.X)
        self.pack(side = tk.BOTTOM)

    def set(self, msg):
        self.label.config(text = msg)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
