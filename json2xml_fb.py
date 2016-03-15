# python json2xml_fb.py  GIST_FB/gist_all_posts_and_comments.json

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
        self.body = re.sub("[^a-zA-Z0-9 ,.!:'\"-+@$%;&# ]","", self.body)
        self.parentid = parentid
        self.ups = ups
        self.downs = downs
        #sys.stderr.write(parent_id+" upvotes:"+str(ups)+"\n")

    def printXML(self,out):
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+str(self.timestamp)+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body>\n<upvotes>"+str(self.ups)+"</upvotes>\n<downvotes>"+str(self.downs)+"</downvotes>\n</post>\n")



json_file = sys.argv[1]
sys.stderr.write("Reading "+json_file+"\n")

postcountperthread = dict() # key is thread_id, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

#f=open(json_file)
#json_string=f.readline()

postsperthread = dict()
# dictionary with thread_id as key and posts dictionary ((author,timestamp)->postid) as value

for json_string in fileinput.input([json_file]):
    json_string = re.sub("}{","},{",json_string)
    parsed_json = json.loads(json_string)
    for item in parsed_json:
        #print item

        if 'is_hidden' in item and not 'picture' in item:
            # these are the opening posts, we exclude the posts with pictures
            author = item['from']
            authorid = author['id']
            authorname = author['name']
            timestamp = item['created_time']
            threadid = item['id']
            #votes = item['like_count']
            thread = Thread(threadid,"","","")
            content =""
            if 'message' in item:
                content = item['message'].encode('utf-8').strip()
            openingpost = Post(threadid,authorname,timestamp,content,"",0,0) # openingpost has threadid as postid
            thread.addPost(openingpost)
            if 'comments' in item:
                responses = item['comments']
                comments = responses['data']
                #print posts
                for comment in comments:
                    #print comment
                    rauthor = comment['from']
                    rauthorid = rauthor['id']
                    rauthorname = rauthor['name']
                    rtimestamp = comment['created_time']
                    rvotes = comment['like_count']
                    postid = comment['id']
                    rcontent = comment['message'].encode('utf-8').strip()
                    parentid = threadid
                    post = Post(postid,rauthorname,rtimestamp,rcontent,parentid,rvotes,0)
                    thread.addPost(post)


        out = open("GIST_FB/threads/"+threadid+".xml","w")
        out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
        out.write("<forum type=\"fb\">\n")


        sys.stderr.write(threadid+"\n")

        thread.printXML(out)
        out.write("</forum>\n")
        out.close()
    



