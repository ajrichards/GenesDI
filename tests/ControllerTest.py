import sys,os,unittest,time,re
from gdiqt4 import Controller

import numpy as np

## test class for the main window function
class ControllerTest(unittest.TestCase):

    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'tests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'gdi':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        self.controller = Controller()
        self.controller.initialize_project("utest")
        self.testFilePathName = os.path.join(BASEDIR,"tests","example_data", "simple_mmu_list.csv")
        self.fileName ="simple_mmu_list.csv"

    def testLog(self):
        self.controller.create_new_project(view=None,projectID='utest')
        self.controller.save()
        self.assertTrue(os.path.isfile(os.path.join(self.controller.homeDir,"%s.log"%self.controller.projectID)))

    def testCreateNewProject(self):   
        self.controller.create_new_project(view=None,projectID='utest')
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"data")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"figs")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"models")))

    def testGeneListFetching(self):
        self.controller.model.load_files([self.testFilePathName])
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,"data"))) != 1)
        fName = re.sub('\s+','_',os.path.split(self.fileName)[-1])
        fName = re.sub('\.csv|\.txt','',fName)
        geneList = self.controller.model.get_genes(fName)
        self.assertEqual(len(geneList),7)
    
### Run the tests 
if __name__ == '__main__':
    unittest.main()
