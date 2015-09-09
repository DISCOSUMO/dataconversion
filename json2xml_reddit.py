# python json2xml_reddit.py reddit_data/2015/RC_2015-04.10000 > reddit_data/2015/RC_2015-04.10000.xml

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

    def __init__(self,threadid,category,ttype):
        self.threadid = threadid
        self.posts = []
        self.category = category
        self.ttype = ttype

    def addPost(self,post):
        self.posts.append(post)

    def getNrOfPosts(self):
        return len(self.posts)

    def printXML(self,out):
        out.write("<thread id=\""+self.threadid+"\">\n<category>"+self.category+"</category>\n<posts>\n")
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
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+self.timestamp+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body>\n<upvotes>"+str(self.ups)+"</upvotes>\n<downvotes>"+str(self.downs)+"</downvotes>\n</post>\n")


json_file = sys.argv[1]
sys.stderr.write("Reading "+json_file+"\n")

postcountperthread = dict() # key is thread_id, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

#f=open(json_file)
#json_string=f.readline()


i=0

# for efficiency reasons, we first read the json file once and count the nr of posts per thread 
# (the posts are ordered by timestamp, not by thread)
# then when we go over all thread_ids in a second round, we can print a thread as soon as we have seen all posts

#while json_string:
for json_string in fileinput.input([json_file]):
    i=i+1
    if (i%10000==0):
        sys.stderr.write(str(i)+" lines read\n")

    parsed_json = json.loads(json_string)
    jsonforlinenr[i] = parsed_json
    
    thread_id = re.sub("t[0-9]_","",parsed_json['link_id'])
    if (thread_id in postcountperthread.keys()) :
        postcountperthread[thread_id] = postcountperthread[thread_id] +1
    else :
        postcountperthread[thread_id] = 1
        #sys.stderr.write("new thread: "+thread_id+"\n")



#    json_string = f.readline()

#f.close()

threads = dict()  # key is thread_id, value is Object thread
postcountseen = dict() # key is thread_id, value is the number of posts that we saw. Once it equals the total nr of posts for the thread, then the thread is printed

sys.stderr.write("Parsing and printing threads\n")
#print("<forum type=\"reddit\">")
for j in range(1,i) :
#    sys.stderr.write(str(j)+"\n");

    if (j%1000==0):
         sys.stderr.write(str(j)+" items parsed\n")

    parsed_json = jsonforlinenr[j]

    subreddit = parsed_json['subreddit']

    if (not os.path.exists("reddit_data/per_subreddit/"+subreddit)) :
        os.makedirs("reddit_data/per_subreddit/"+subreddit)
  
    thread_id = re.sub("t[0-9]_","",parsed_json['link_id'])
    # the post with the same id as the thread id, is the opening post
    
    out = open("reddit_data/per_subreddit/"+subreddit+"/"+thread_id+".xml","w")

    out.write("<?xml version=\"1.0\"?>\n")
    out.write("<forum type=\"reddit\">\n")
    author = parsed_json['author']
    timestamp = parsed_json['created_utc']

    post_id = parsed_json['id']
    body = parsed_json['body'].encode('utf-8').strip()
    parent_id = re.sub("t[0-9]_","",parsed_json['parent_id'])
    downs = parsed_json['downs']
    ups = parsed_json['ups']

#    sys.stderr.write(thread_id+" upvotes:"+str(ups)+"\n")
    post = Post(post_id,author,timestamp,body,parent_id,ups,downs)


    if (thread_id in threads.keys()) :
        thread = threads[thread_id]
        thread.addPost(post)
        postcountseen[thread_id] = postcountseen[thread_id] +1
    else :
        thread = Thread(thread_id,subreddit,"")
        threads[thread_id] = thread
        thread.addPost(post)
        postcountseen[thread_id] = 1
        
#    sys.stderr.write(">>>>> TOTAL of posts in thread "+thread_id+":"+str(postcountperthread[thread_id])+"\n")
#    sys.stderr.write(">>>>> CURRENT nr of posts in thread: "+thread_id+":"+str(thread.getNrOfPosts())+"\n")
    if (postcountseen[thread_id] >= postcountperthread[thread_id]) :
        #sys.stderr.write("print thread "+thread_id+"\n")
        thread.printXML(out)
 
    out.write("</forum>\n")

    out.close()

#print("</forum>")
    



