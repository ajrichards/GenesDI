import sys,os,unittest,time,re
import subprocess
from gdiqt4 import Model
from gdiqt4 import get_gene_list_names

import numpy as np

## test class for the main window function
class ModelTest(unittest.TestCase):
       
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'tests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'gdi':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        self.projectID = 'utest'
        self.homeDir = os.path.join(BASEDIR,"gdiqt4","projects",self.projectID)
        self.model = Model()
        self.model.initialize(self.projectID, self.homeDir)
        self.testFilePathName = os.path.join(BASEDIR,"tests","example_data", "simple_mmu_list.csv") 
        self.fileName ="simple_mmu_list.csv"
        self.assertTrue(os.path.isfile(self.testFilePathName))
    
    def testLoadFile(self):
        ## test that events and channels may be retrieved
        self.model.load_files([self.testFilePathName])
        fName = re.sub('\s+','_',os.path.split(self.fileName)[-1])
        fName = re.sub('\.csv|\.txt','',fName)
        geneList = self.model.get_genes(fName)
        self.assertEqual(len(geneList),7)
    
    def testGetAllGeneLists(self):
        allGeneLists = get_gene_list_names(self.homeDir)
        self.assertEqual(len(allGeneLists),1)


### Run the tests 
if __name__ == '__main__':
    unittest.main()
