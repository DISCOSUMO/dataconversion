# python json2xml_viva.py viva_data/viva_dump  > viva_data/viva_dump.xml


import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import json
import dicttoxml
import re
import fileinput
from collections import defaultdict
from BeautifulSoup import BeautifulSoup as BSHTML

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

    def printXML(self):
        print("<thread id=\""+self.threadid+"\">\n<category>"+self.category+"</category>\n<posts>")
        for post in self.posts:
            post.printXML()
        print("</posts>\n</thread>")


class Post:
    postid=""
    author=""
    timestamp=""
    body=""
    parent_id=""

    def __init__(self,postid,author,timestamp,body,parentid):
        self.postid = postid
        self.author = author
        self.timestamp = timestamp
        self.body = body
        self.parentid = parentid
    
    def printXML(self):
        print("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+self.timestamp+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body></post>")


json_file = sys.argv[1]
sys.stderr.write("Reading "+json_file+"\n")

postcountperthread = dict() # key is thread_id, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

#f=open(json_file)
#json_string=f.readline()



print("<forum type=\"viva\">")
#while json_string:
for json_string in fileinput.input([json_file]):
    
    json_string = re.sub("\": \"","\":\"",json_string)
#    sys.stderr.write(json_string+"\n")
    parsed_json = json.loads(json_string)
    for json_thread in parsed_json:
        thread_id = json_thread['thread_id']
        category = json_thread['category']
        thread = Thread(thread_id,category,"")

        htmlcontent = json_thread['content']
        
#        sys.stderr.write(thread_id+"\n")    

        htmlstruct = BSHTML(htmlcontent)
        nrofposts = len(htmlstruct.findAll('span'))
        sys.stderr.write(thread_id+": nr of posts:"+str(nrofposts)+"\n")
        i = 0
        while (i < nrofposts) :
            timestamp = htmlstruct.findAll('span')[i].contents[0].strip()
            author = htmlstruct.findAll('strong')[i].contents[0].strip()
            content = htmlstruct.findAll('p')[i].contents[0]
            #sys.stderr.write(thread_id+"\t"+timestamp+"\t"+author+"\n")     
            post = Post(str(i),author,timestamp,content,"")
            thread.addPost(post)
            i = i+1

        thread.printXML()


print("</forum>")
    



