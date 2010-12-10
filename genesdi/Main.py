#!/usr/bin/python

'''
this script activates the GUI

A. Ricahrds
'''

import sys, getopt, os
from PyQt4 import QtGui
from gdiqt4.qtlib import MainWindow

class Main():
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        app.setOrganizationName("Medical University of South Carolina")
        app.setOrganizationDomain("musc.edu")
        app.setApplicationName("gdiqt4")
        mw = MainWindow()
        mw.show()
        app.exec_()

if __name__ == '__main__':
    main = Main()
