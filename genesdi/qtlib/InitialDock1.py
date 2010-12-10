import sys
from PyQt4 import QtGui, QtCore

class InitialDock1(QtGui.QWidget):
    def __init__(self, parent=None, message=None, speciesDefault=None, contBtnFn=None, addBtnFn=None, speciesFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Data Processing')
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        hbox4 = QtGui.QHBoxLayout()
        hbox4.setAlignment(QtCore.Qt.AlignCenter)

        self.speciesList = ['S. cerevisiae', 'M. musculus', 'H. sapiens']


        ## message
        if message != None:
            label = QtGui.QLabel(message)
            hbox1.addWidget(label)
            vbox.addLayout(hbox1)

        ## add gene list button
        if addBtnFn != False:
            self.addBtn = QtGui.QPushButton("Add Gene List")
            self.addBtn.setMaximumWidth(100)
            self.addBtn.setMinimumWidth(100)
            hbox4.addWidget(self.addBtn)
            vbox.addLayout(hbox4)

            if addBtnFn != None:
                self.connect(self.addBtn, QtCore.SIGNAL('clicked()'),addBtnFn)

        ## cont button
        if contBtnFn != False:
            self.contBtn = QtGui.QPushButton("Continue")
            self.contBtn.setMaximumWidth(100)
            self.contBtn.setMinimumWidth(100)
            hbox3.addWidget(self.contBtn)
            vbox.addLayout(hbox3)
            
            if contBtnFn != None:
                self.connect(self.contBtn, QtCore.SIGNAL('clicked()'),contBtnFn)
        
        ## species selector         
        if speciesFn != False:
            hbox1.addWidget(QtGui.QLabel('Species Selector'))
            hbox1.setAlignment(QtCore.Qt.AlignTop)
            vbox.addLayout(hbox1)
            self.speciesSelector = QtGui.QComboBox(self)
            self.speciesSelector.setMaximumWidth(150)
            for species in self.speciesList:
                self.speciesSelector.addItem(species)
            hbox2.addWidget(self.speciesSelector)
            hbox2.setAlignment(QtCore.Qt.AlignCenter)
            vbox.addLayout(hbox2)

            if speciesDefault != None:
                if self.speciesList.__contains__(speciesDefault):
                    self.speciesSelector.setCurrentIndex(self.speciesList.index(speciesDefault))
                else:
                    print "ERROR: in dpd - bad specified speciesDefault"

            if speciesFn != None:
                self.connect(self.speciesSelector,QtCore.SIGNAL('activated(QString)'), speciesFn)

        ## finalize layout
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

    def enable_add_btn(self,fn):
        self.connect(self.contBtn, QtCore.SIGNAL('clicked()'),fn)

    def enable_continue_btn(self,fn):
        self.connect(self.contBtn, QtCore.SIGNAL('clicked()'),fn)

    def disable_all(self):
        pass

    def enable_all(self):
        pass

### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    id1 = InitialDock1()
    id1.show()
    sys.exit(app.exec_())
    
