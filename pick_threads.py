# python pick_threads.py 200 reddit_data/per_subreddit/ reddit_data/samples/1000randomthreads
# python pick_threads.py 10 reddit_data/per_subreddit/ reddit_data/samples/questions questions.config.xml
# python pick_threads.py 1000 reddit_data/per_subreddit/ reddit_data/samples/1000long10threads long.config.xml
# python pick_threads.py 1000 Viva_forum/per_category/ reddit_data/samples/1000long20threads long.config.xml


import os, random
import sys
import shutil
import re
from random import randint
import xml.etree.ElementTree as ET


rootdir = sys.argv[2]
nofiles = sys.argv[1]
resultdir = sys.argv[3]

minpostcount = 0
maxpostcount = sys.maxint
random = True

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def countpostsinthread(fn):
    pct=0
    f = open(fn,'r')
    for line in f:
        if "<post " in line:
            pct += 1
    return pct

if len(sys.argv) > 4:
    configfile = sys.argv[4]
    tree = ET.parse(configfile)
    root = tree.getroot()
    random = str2bool(root.find('random').text)
    thread = root.find('thread')
    minpostcount = int(thread.find('postcount').find('min').text)
    maxpostcount = int(thread.find('postcount').find('max').text)
    print configfile, random, minpostcount, maxpostcount

#verberne@pipsqueak:~/Projects/DISCOSUMO/dataconversion/Viva_forum/per_category$ grep "<post " */*.xml | sed 's/:.*//' | uniq -c > ../../postcountperthread.viva.txt
#verberne@pipsqueak:~/Projects/DISCOSUMO/dataconversion$ cat postcountperthread.viva.txt | perl -e 'while(<>){s/^ *//; s/([0-9]+)  *(.*)/$2\t$1/; s/^.*\///; print;}' > l
#verberne@pipsqueak:~/Projects/DISCOSUMO/dataconversion$ mv l postcountperthread.viva.txt

postcountfilename = "../dataconversion/postcountperthread.reddit.txt"
if re.match(".*Viva.*",rootdir):
    postcountfilename = "../dataconversion/postcountperthread.viva.txt"

sys.stderr.write("postcountfile:"+postcountfilename+"\n")

postcounts = dict()
sys.stderr.write("Read postcountperthread file\n")
with open(postcountfilename,"r") as postcountfile:
    for line in postcountfile:
        parts = line.rstrip().split("\t")
        filename = parts[0]
        postcount = parts[1]
        postcounts[filename] = int(postcount)


postcountfile.close()



if random:
    sys.stderr.write("Read all files that match the criteria in dict\n")

    allfiles = dict()

    n=0
    for subdir in os.listdir(rootdir) :
        for f in os.listdir(rootdir+"/"+subdir) :
            if f.endswith("xml"):
                pc = postcounts[f]
                if minpostcount <= pc <= maxpostcount:
                    #sys.stderr.write(f+"\n")
                    allfiles[n] = rootdir+"/"+subdir+"/"+f
                    n += 1

    sys.stderr.write("Pick threads\n")

    pc = 0
    for j in range(0,int(nofiles)) :
        i = randint(0,n)
        while i not in allfiles:
            i = randint(0,n)
        randfile = allfiles[i]
        randfilename = re.sub("^.*/","",randfile)
        copyfrom = randfile
        copyto = resultdir+"/"+randfilename
        del allfiles[i]
        print i,randfile
        shutil.copy(copyfrom,copyto)

