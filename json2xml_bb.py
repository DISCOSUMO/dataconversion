# python json2xml_fb.py  Forum_directory

import os
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import json
#import dicttoxml
import re
import fileinput
from collections import defaultdict
#from BeautifulSoup import BeautifulSoup as BSHTML

directory = sys.argv[1]
json_forums_file = directory+"/wp_bb_forums.json"
json_topics_file = directory+"/wp_bb_topics.json"
json_posts_file = directory+"/wp_bb_posts.json"

class Forum:
    def __init__ (self,forum_id,name,description):
        self.forum_id = forum_id
        self.name = name
        self.description = description

    def addThread(self,thread):
        self.threads.append(thread)

    def getNrOfThreads(self):
        return len(self.threads)

    def printXML(self,out):
        out.write('<forum type="bb" id="'+self.forum_id+'>\n')
        out.write('<name>'+self.name+'</name>')
        out.write('<description>'+self.description+'</description>')
        for thread in self.threads:
            thread.printXML(out)
        out.write('</forum>')


class Thread:

    def __init__(self,thread_id,title,category,ttype):
        self.thread_id = thread_id
        self.title = title
        self.posts = []
        self.category = category
        self.ttype = ttype

    def addPost(self,post):
        self.posts.append(post)

    def getNrOfPosts(self):
        return len(self.posts)

    def printXML(self,out):
        out.write("<thread id=\""+self.thread_id+"\">\n<category>"+self.category+"</category>\n<title>"+self.title+"</title>\n<posts>\n")
        for post in self.posts:
            post.printXML(out)
        out.write("</posts>\n</thread>\n")


class Post:
    postid=""
    author=""
    timestamp=""
    body=""
    parent_id=""

    def __init__(self,postid,author,timestamp,body,parentid,ups,downs):
        self.postid = postid
        self.author = author
        self.timestamp = timestamp
        self.body = re.sub("#","&#35;",body)
        self.body = re.sub("&","&amp;",self.body)
        self.body = re.sub("<","&lt;",self.body)
        self.body = re.sub(">","&gt;",self.body)
        self.body = re.sub("=","&#61;",self.body)
        self.body = re.sub("http[^ ]*","[URL]",self.body)
        #self.body = re.sub(r'[^a-zA-Z0-9 \\,.!:\'"-+@$%;&?#]',"", self.body)
        self.parentid = parentid
        self.ups = ups
        self.downs = downs
        #sys.stderr.write(parent_id+" upvotes:"+str(ups)+"\n")

    def printXML(self,out):
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+str(self.timestamp)+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body>\n<upvotes>"+str(self.ups)+"</upvotes>\n<downvotes>"+str(self.downs)+"</downvotes>\n</post>\n")

sys.stderr.write("Reading "+json_forums_file+"\n")

forum_names = dict()

json_string = ""
with open(json_forums_file) as f:
    for line in f:
        if not re.match("^//",line):
            json_string += line.rstrip()
    parsed_json = json.loads(json_string)
    for item in parsed_json:
        forum_id = item['forum_id']
        forum_name = item['forum_name']
        forum_names[forum_id] = forum_name
        forum_desc = item['forum_desc']
        forum = Forum(forum_id,forum_name,forum_desc)
        #print(forum.forum_id,forum_name,forum.description)

posts_per_thread = dict()

json_string = ""
with open(json_posts_file) as f:
    for line in f:
        if not re.match("^//",line):
            json_string += line.rstrip()
    parsed_json = json.loads(json_string)
    for item in parsed_json:

    # def __init__(self,postid,author,timestamp,body,parentid,ups,downs):

        post_id = item['post_id']
        threadid = item['topic_id']
        author = item['poster_id']
        timestamp = item['post_time']
        body = item['post_text']
        post = Post(post_id,author,timestamp,body,threadid,0,0)
        postsforthisthread = list()
        if threadid in posts_per_thread:
            postsforthisthread = posts_per_thread[threadid]
        postsforthisthread.append(post)
        posts_per_thread[threadid] = postsforthisthread


json_string = ""
with open(json_topics_file) as f:
    for line in f:
        if not re.match("^//",line):
            json_string += line.rstrip()
    parsed_json = json.loads(json_string)
    for item in parsed_json:
        forum_id = item['forum_id']
        forum_name = forum_names[forum_id]
        threadid = item['topic_id']
        title = item['topic_title']
        forum_id = item['forum_id']
        thread = Thread(threadid,title,forum_id,"")
        #print(thread.thread_id,thread.title,thread.category)
        if threadid in posts_per_thread:
            postsforthisthread = posts_per_thread[threadid]
            for post in postsforthisthread:
                thread.addPost(post)
        else:
            print ("thread has no posts")

        out = open(directory+"/threads/"+threadid+".xml","w")
        out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
        out.write("<forum type=\"bb\" name=\"'"+forum_name+"\">\n")


        sys.stderr.write(threadid+"\n")

        thread.printXML(out)
        out.write("</forum>\n")
        out.close()




