#!/usr/bin/python 
import unittest,sys,os,getopt

import matplotlib
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')

## change working dir
os.chdir(os.path.join(".","cytostream"))
sys.path.append(os.path.join("..","unittests","data"))

from unittests import *
unittest.main()
