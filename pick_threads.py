# python pick_threads.py 200 reddit_data/per_subreddit/ reddit_data/samples/1000randomthreads

import os, random
import sys
import shutil
import re
from random import randint

rootdir = sys.argv[2]
nofiles = sys.argv[1]
resultdir = sys.argv[3]

allfiles = dict()

i=0
for subdir in os.listdir(rootdir) :
    for file in os.listdir(rootdir+"/"+subdir) :
        allfiles[i] = rootdir+"/"+subdir+"/"+file
        i += 1

n = len(allfiles)-1

for j in range(0,int(nofiles)) :
    #randdir = random.choice(os.listdir(rootdir))
    #print randdir
    i = randint(0,n)
    randfile = allfiles[i]
    copyfrom = randfile
    randfile = re.sub("^.*/","",randfile)
    copyto = resultdir+"/"+randfile
    while re.match("authors.list",randfile) or os.path.isfile(copyto) :
        i = randint(0,len(allfiles)-1)
        randfile = allfiles[i]
        copyfrom = randfile
        randfile = re.sub("^.*/","",randfile)
        copyto = resultdir+"/"+randfile
    print i,randfile
    shutil.copy(copyfrom,copyto)

