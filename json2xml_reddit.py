# python json2xml_reddit.py reddit_data/reddit_openingposts/RS_2014-12.1000 reddit_data/2014/RC_2014-12.100000 > reddit_data/RSC_2014-12.1000.xml

import os
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import json
import dicttoxml
import re
import fileinput
from collections import defaultdict

class Thread:

    def __init__(self,threadid,category,ttype,title):
        self.threadid = threadid
        self.posts = []
        self.category = category
        self.ttype = ttype
        self.title = title

    def addPost(self,post):
        self.posts.append(post)

    def getNrOfPosts(self):
        return len(self.posts)

    def printXML(self,out):
        out.write("<thread id=\""+self.threadid+"\">\n<category>"+self.category+"</category>\n<title>"+self.title+"</title>\nposts>\n")
        for post in self.posts:
            post.printXML(out)
        out.write("</posts>\n</thread>\n")


class Post:

    def __init__(self,postid,author,timestamp,body,parentid,ups,downs):
        self.postid = postid
        self.author = author
        self.timestamp = timestamp
        self.body = body
        self.parentid = parentid
        self.ups = ups
        self.downs = downs
        #sys.stderr.write(parent_id+" upvotes:"+str(ups)+"\n")
    
    def printXML(self,out):
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+str(self.timestamp)+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body>\n<upvotes>"+str(self.ups)+"</upvotes>\n<downvotes>"+str(self.downs)+"</downvotes>\n</post>\n")


######### READING RS FILE: FILE WITH OPENING POSTS (SUBMISSIONS) ###########

json_S_file = sys.argv[1]
sys.stderr.write("Reading "+json_S_file+"\n")

thread_ids = set() # list of thread ids, to find if we have the opening post for a given comment
threads = dict()  # key is thread_id, value is Object thread, to find the thread given the thread id

i=0
for json_string in fileinput.input([json_S_file]):
    i=i+1
    if (i%10000==0):
        sys.stderr.write(str(i)+" lines read\n")

    parsed_json = json.loads(json_string)
    
    thread_id = parsed_json['id']
 #   sys.stderr.write("thread id:"+thread_id+"\n")
    subreddit = parsed_json['subreddit']
    title = parsed_json['title']
    thread = Thread(thread_id,subreddit,"",title)

    thread_ids.add(thread_id)
    threads[thread_id] = thread

    # Add the opening post of the thread as post to the thread:
    
    if 'author' in parsed_json:
        author = parsed_json['author']
    else:
        author = ""

    timestamp = parsed_json['created_utc']
    body = parsed_json['selftext']
    parent_id = ""
    downs = parsed_json['downs']
    ups = parsed_json['ups']

    post = Post(thread_id,author,timestamp,body,parent_id,ups,downs)
    thread.addPost(post)


######### READING RC FILE: FILE WITH COMMENTS ###########

json_C_file = sys.argv[2]
sys.stderr.write("Reading "+json_C_file+"\n")

postcountperthread = dict() # key is thread_id, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

# for efficiency reasons, we first read the comments file once and count the
# nr of posts per thread (the posts are ordered by timestamp, not by thread)
# then when we go over all thread_ids in a second round, we can print a 
# thread as soon as we have seen all posts

#tmpfile = json_C_file+".tmp"
#tmp = open(tmpfile,"w")


i=0
submissionpresent = 0

for json_string in fileinput.input([json_C_file]):
    i=i+1
    if (i%10000==0):
        sys.stderr.write(str(i)+" lines read\n")

    parsed_json = json.loads(json_string)
    jsonforlinenr[i] = parsed_json
    
    thread_id = re.sub("t[0-9]_","",parsed_json['link_id'])
#    parent_id = re.sub("t[0-9]_","",parsed_json['parent_id'])
#    sys.stderr.write("thread id for comment:"+thread_id+"\n")
#    sys.stderr.write("parent id for comment:"+parent_id+"\n")

#    if (thread_id in threads.keys()) :
    if (thread_id in thread_ids) :
#        sys.stderr.write("We have the opening post for this thread: "+thread_id+"\n")
#        tmp.write(json_string)
        submissionpresent = submissionpresent +1
        if (submissionpresent%1000==0) :
            sys.stderr.write(str(submissionpresent)+" comments found for which we have the original submission\n")

        if (thread_id in postcountperthread.keys()) :
            postcountperthread[thread_id] = postcountperthread[thread_id] +1
        else :
            postcountperthread[thread_id] = 2 # the opening post is the first. the first comment is the second

#tmp.close()

percwithsubmission = 100 * float(submissionpresent)/float(i)
sys.stderr.write("Total nr of comments: "+str(i)+". For "+str(percwithsubmission)+"% of the comments we have the original submission\n")


######### READING TMP FILE WITH COMMENTS FOR WHICH WE HAVE THE ORIGINAL SUBMISSION ###########


sys.stderr.write("Parsing and printing comment threads\n")

#print("<forum type=\"reddit\">")
for j in range(1,i) :
    if (j%100==0) :
        sys.stderr.write(str(j)+" items of "+str(i)+" parsed\n");

#for json_string in fileinput.input([tmpfile]):
    parsed_json = jsonforlinenr[j]

#    parsed_json = json.loads(json_string)

    thread_id = re.sub("t[0-9]_","",parsed_json['link_id'])
    

    if (thread_id in thread_ids) :
        
        subreddit = parsed_json['subreddit']
        author = parsed_json['author']
        timestamp = parsed_json['created_utc']

        post_id = parsed_json['id']
        body = parsed_json['body'].encode('utf-8').strip()
        parent_id = re.sub("t[0-9]_","",parsed_json['parent_id'])
        downs = parsed_json['downs']
        ups = parsed_json['ups']

    #    sys.stderr.write(thread_id+" upvotes:"+str(ups)+"\n")
        post = Post(post_id,author,timestamp,body,parent_id,ups,downs)

        thread = threads[thread_id]
        thread.addPost(post)
# we only add a post to a thread if we have the opening post (from the RS file)

#    else :
#        thread = Thread(thread_id,subreddit,"")
#        threads[thread_id] = thread
#        thread.addPost(post)
        
        sys.stderr.write("TOTAL nr of posts in thread "+thread_id+":"+str(postcountperthread[thread_id])+"\n")
        sys.stderr.write("CURRENT nr of posts in thread: "+thread_id+":"+str(thread.getNrOfPosts())+"\n")
        if (thread.getNrOfPosts() >= postcountperthread[thread_id]) :
            sys.stderr.write("print thread "+thread_id+"\n")

            if (not os.path.exists("reddit_data/per_subreddit/"+subreddit)) :
                os.makedirs("reddit_data/per_subreddit/"+subreddit)
 
            out = open("reddit_data/per_subreddit/"+subreddit+"/"+thread_id+".xml","w")

            out.write("<?xml version=\"1.0\"?>\n")
            out.write("<forum type=\"reddit\">\n")

            thread.printXML(out)
 
            out.write("</forum>\n")

            out.close()

#print("</forum>")
    



