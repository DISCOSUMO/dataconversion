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

postcountperthread = dict() # key is threadid, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

#f=open(json_file)
#json_string=f.readline()

postsperthread = {}
# dictionary with threadid as key and posts dictionary ((author,timestamp)->postid) as value

months_conversion = {'januari': '01', 'februari': '02', 'maart': '03', 'april': '04', 'mei': '05', 'juni': '06', 'juli': '07', 'augustus': '08', 'september': '09', 'oktober': '10', 'november': '11', 'december': '12'}

def findQuote (content,threadid) :
    pattern = re.compile("\*\*\[(.*) schreef op (.*) @\\n([0-9:]+)\]")
    match = pattern.search(content)
    referred_post = ""
    if (match) :
        user = match.group(1)
        date = match.group(2)
        time = match.group(3)
        [day,month,year] = date.split();
        monthnumber = months_conversion[month]
        converteddate = day+"-"+monthnumber+"-"+year+" "+time
        postsforthread = postsperthread[threadid]
        if ((user,converteddate) in postsforthread.keys()) :
            referred_post = postsforthread[(user,converteddate)]
        else :
            sys.stderr.write("Quoted post is missing from thread: "+user+" "+converteddate+"\n")
    return referred_post


print("<?xml version=\"1.0\"?>\n")
print("<forum type=\"viva\">")
#while json_string:
for json_string in fileinput.input([json_file]):
    
    json_string = re.sub("\": \"","\":\"",json_string)
#    sys.stderr.write(json_string+"\n")
    parsed_json = json.loads(json_string)
    for json_thread in parsed_json:

        posts = {} 
        # dictionary with (author,timestamp) as key and postid as value, for finding referenced posts in quotes

        threadid = json_thread['thread_id']
        category = json_thread['category']
        thread = Thread(threadid,category,"")

        htmlcontent = json_thread['content']
        
#        sys.stderr.write(threadid+"\n")    

        htmlstruct = BSHTML(htmlcontent)
        nrofposts = len(htmlstruct.findAll('span'))
        sys.stderr.write(threadid+": nr of posts:"+str(nrofposts)+"\n")
        i = 0
        while (i < nrofposts) :
            timestamp = htmlstruct.findAll('span')[i].contents[0].strip()
            author = htmlstruct.findAll('strong')[i].contents[0].strip()
            content = htmlstruct.findAll('p')[i].contents[0]
            parentid = findQuote(content,threadid)
            #sys.stderr.write(threadid+"\t"+timestamp+"\t"+author+"\n")     
            post = Post(str(i),author,timestamp,content,str(parentid))
            thread.addPost(post)
            posts[(author,timestamp)] = i;
            postsperthread[threadid] = posts;
            i = i+1

        thread.printXML()


print("</forum>")
    




