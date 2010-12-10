import sys
from PyQt4 import QtGui, QtCore

class OpenExistingProject(QtGui.QWidget):
    def __init__(self, projectList, parent=None, openBtnFn=None,closeBtnFn=None,rmBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        dirModel  = QtGui.QDirModel()

        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl2 = QtGui.QHBoxLayout()
        self.hbl2.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl3 = QtGui.QHBoxLayout()
        self.hbl3.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl4 = QtGui.QHBoxLayout()
        self.hbl4.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl5 = QtGui.QHBoxLayout()
        self.hbl5.setAlignment(QtCore.Qt.AlignCenter)

        self.hbl1.addWidget(QtGui.QLabel('Choose an existing project'))

        self.projectSelector = QtGui.QComboBox(self)
        self.projectSelector.setMaximumWidth(200)
        self.projectSelector.setMinimumWidth(200)
        for project in projectList:
            self.projectSelector.addItem(project)
        self.hbl2.addWidget(self.projectSelector)

        
        self.openBtn = QtGui.QPushButton("Open project", self)
        self.openBtn.setMaximumWidth(200)
        self.openBtn.setMinimumWidth(200)
        self.hbl3.addWidget(self.openBtn)
        if openBtnFn == None:
            openBtnFn = self.generic_callback

        self.connect(self.openBtn,QtCore.SIGNAL('clicked()'), openBtnFn)

        self.closeBtn = QtGui.QPushButton("Close screen", self)
        self.closeBtn.setMaximumWidth(200)
        self.closeBtn.setMinimumWidth(200)
        self.hbl4.addWidget(self.closeBtn)
        if closeBtnFn == None:
            closeBtnFn = self.generic_callback

        self.connect(self.closeBtn, QtCore.SIGNAL('clicked()'),closeBtnFn)
        
        self.rmBtn = QtGui.QPushButton("Delete selected project", self)
        self.rmBtn.setMaximumWidth(200)
        self.rmBtn.setMinimumWidth(200)
        self.hbl5.addWidget(self.rmBtn)
        if rmBtnFn == None:
            rmBtnFn = self.generic_callback

        self.connect(self.rmBtn, QtCore.SIGNAL('clicked()'),rmBtnFn)
        

        # finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
        self.vbl.addLayout(self.hbl3)
        self.vbl.addLayout(self.hbl4)
        self.vbl.addLayout(self.hbl5)
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.vbl)

    def generic_callback(self):
        print 'This button does nothing'

    def get_selected_project(self):
        spInd = self.projectSelector.currentIndex()
        sp = str(self.projectSelector.currentText())
        #sm = sm + ".pickle"

        return sp, spInd
    


### Run the tests                                                                                                                                                                
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    projectList = ['project1','project2','project3']
    oep = OpenExistingProject(projectList)
    oep.show()
    sys.exit(app.exec_())
    
