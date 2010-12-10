import sys,re
from PyQt4 import QtGui, QtCore

class GeneListSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of files and models. Upon selection variables corresponding to the
    selected files are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, fileList, color='white', parent=None, modelsRun=None, fileDefault=None, selectionFn=None, 
                 showModelSelector=False, modelDefault=None,possibleModels=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)
        self.modelSelector = None
        self.modelsRun = modelsRun
        self.color = color
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        
        ## error checking
        if showModelSelector == True and self.modelsRun == None:
            print "ERROR: must specify modelsRun if ModelSelector is true"

        ## file selector
        hbox1.addWidget(QtGui.QLabel('Gene Set Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        self.fileSelector = QtGui.QComboBox(self)
        
        fileList = [re.sub("\.fcs","",f) for f in fileList]
        for fileName in fileList:
            self.fileSelector.addItem(fileName)

        hbox2.addWidget(self.fileSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)

        if fileDefault != None:
            fileDefault = re.sub("\.fcs","",fileDefault)
            if fileList.__contains__(fileDefault):
                self.fileSelector.setCurrentIndex(fileList.index(fileDefault))
            else:
                print "ERROR: in file selector - bad specified fileDefault", fileDefault

        if selectionFn == None:
            selectionFn = self.generic_callback
        self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)    

        ## finalize layout                           
        vbox.setAlignment(QtCore.Qt.AlignTop)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        if showModelSelector == True:
             vbox.addLayout(hbox3)
             vbox.addLayout(hbox4)
    
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def set_refresh_thumbs_fn(self,refreshFn):
        self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn)
        if self.modelSelector != None:
            self.connect(self.modelSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn) 
        

    def get_selected_file(self):
        sfInd = self.fileSelector.currentIndex()
        sf = str(self.fileSelector.currentText())

        return sf+".fcs", sfInd

    def get_selected_model(self):
        smInd = self.modelSelector.currentIndex()
        sm = str(self.modelSelector.currentText())
        
        return sm, smInd

    def generic_callback(self):
        print 'callback does not do anything yet'


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    allGeneLists = ['geneList1', 'geneList2','geneList3','geneList4']
    fs = GeneListSelector(allGeneLists)
    fs.show()
    sys.exit(app.exec_())
