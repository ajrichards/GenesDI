#!/usr/bin/python

import sys,getopt,os,re,cPickle,time,csv

if len(sys.argv) < 3:
    print sys.argv[0] + " -f filePath -h homeDir -d dataType -t transform"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:d:')
except getopt.GetoptError:
    print sys.argv[0] + "-f filePath -h homeDir -d dataType"
    print "Note: fileName (-f) full file path" 
    print "      homeDir  (-h) home directory for current project"
    print "             k (-d) data type ('csv','txt')"
    sys.exit()

transform = 'log'
filePath = None
homeDir = None
dataType = None
for o, a in optlist:
    if o == '-f':
        filePath = a
    if o == '-h':
        homeDir = a
    if o == '-d':
        dataType = a

## initial error checking
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: not a valid project", homeDir
    sys.exit()

if os.path.isfile(filePath) == False:
    print "INPUT ERROR: file path does not exist", filePath
    sys.exit()

if dataType not in ['csv','txt']:
    print "INPUT ERROR: bad data type specified", dataType
    sys.exit()
    
## variables
projName = os.path.split(homeDir)[-1]

geneList = []
if dataType in ['csv', 'txt']:
    reader = csv.reader(open(filePath,'rb'))
    for linja in reader:
        if len(linja) == 1:
            geneList.append(re.sub("\s+","",linja[0]))

## save the gene list to a pickle file
newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
newFileName = re.sub('\.csv|\.txt','',newFileName)
newDataFileName = newFileName + "_data.pickle"

tmp1 = open(os.path.join(homeDir,'data',newDataFileName),'w')
cPickle.dump(geneList,tmp1)
tmp1.close()

