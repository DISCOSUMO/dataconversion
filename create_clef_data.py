import os
import sys

rootdir = "/Users/suzanverberne/Data/CLEF_social-book-search/reddit/"
orig_traindir = rootdir+"originalthreads/trainingdata"
orig_testdir = rootdir+"originalthreads/testdata"
result_traindir = rootdir+"data/train"
result_testdir = rootdir+"data/test"
subreddits = ('books','suggestmeabook')

sys.stderr.write("Read files in "+orig_traindir+"\n")
for sr in subreddits:
    for f in os.listdir(orig_traindir+'/'+sr):
        if f.endswith("xml"):
            sys.stderr.write("\t"+f+"\n")
            out = open(result_traindir+'/'+f,'w+')
            with open(orig_traindir+'/'+sr+'/'+f,"r") as file:
                for line in file:
                    if "</post>" in line:
                        break
                    out.write(line)
                out.write("</post>\n</posts>\n</thread>\n</forum>")
            sys.stderr.write("Wrote to "+result_traindir+'/'+f+'\n')
            out.close()

sys.stderr.write("Read files in "+orig_testdir+"\n")
for f in os.listdir(orig_testdir+'/threads'):
    if f.endswith("xml"):
        sys.stderr.write("\t"+f+"\n")
        out = open(result_testdir+'/'+f,'w+')
        with open(orig_testdir+'/threads/'+f,"r") as file:
            for line in file:
                if "</post>" in line:
                    break
                if "<category>" in line:
                    out.write("<category>masked</category>\n")
                else:
                    out.write(line)
            out.write("</post>\n</posts>\n</thread>\n</forum>")
        sys.stderr.write("Wrote to "+result_testdir+'/'+f+'\n')
        out.close()
