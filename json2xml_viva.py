# coding=utf-8
#  python json2xml_viva.py Viva_forum/viva_dump.json
# python json2xml_viva.py /Users/suzanverberne/Data/FORUM_DATA/Viva/viva_forum_gezondheid_10000.json

import os
import sys
import json
import re
import fileinput
import BeautifulSoup as BSHTML

json_file = sys.argv[1]
txt_file = json_file+".txt"

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

    def printTXT(self,out):
        for post in self.posts:
            post.printTXT(out)


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
    
    def printXML(self,out):
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+self.timestamp+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body></post>\n")

    def printTXT(self,out):
        out.write(self.body+"\n")


sys.stderr.write("Reading "+json_file+"\n")

postcountperthread = dict() # key is thread_id, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

#f=open(json_file)
#json_string=f.readline()

postsperthread = {}
# dictionary with thread_id as key and posts dictionary ((author,timestamp)->postid) as value

months_conversion = {'januari': '01', 'februari': '02', 'maart': '03', 'april': '04', 'mei': '05', 'juni': '06', 'juli': '07', 'augustus': '08', 'september': '09', 'oktober': '10', 'november': '11', 'december': '12', 'May': '05'}

def findQuote (content,thread_id) :
    pattern = re.compile("\*\*\[(.*) schreef op (.*) @\\n([0-9:]+)\]")
    match = pattern.search(content)
    referred_post = ""
    if match :
        user = match.group(1)
        date = match.group(2)
        time = match.group(3)
        datepattern = re.compile("^[^ ]+ [^ ]+ [^ ]+$")
        if datepattern.match(date) :
            [day,month,year] = date.split()
            monthnumber = months_conversion[month]
            converteddate = day+"-"+monthnumber+"-"+year+" "+time
            if thread_id in postsperthread.keys() :
                postsforthread = postsperthread[thread_id]
            
                if (user,converteddate) in postsforthread.keys() :
                    referred_post = postsforthread[(user,converteddate)]
                else :
                    user = "anoniem"
                    sys.stderr.write("Quoted post is missing from thread: "+user+" "+converteddate+" ")
                    if (user,converteddate) in postsforthread.keys() :
                        referred_post = postsforthread[(user,converteddate)]
                        sys.stderr.write("but found anoniempje at that timestamp and used that\n")
                    else :
                        sys.stderr.write("and could also not find anoniempje at that timestamp\n")
    return referred_post


#print("<?xml version=\"1.0\"?>")
#print("<forum type=\"viva\">")
#while json_string:
outtxt = open(txt_file,'w')
for json_string in fileinput.input([json_file]):
    
    json_string = re.sub("\": \"","\":\"",json_string)
    json_string = re.sub('<strong></strong>', '<strong>XXX</strong>', json_string)
#    sys.stderr.write(json_string+"\n")
    parsed_json = json.loads(json_string)
    for json_thread in parsed_json:

        posts = {} 
        # dictionary with (author,timestamp) as key and postid as value, for finding referenced posts in quotes

        thread_id = json_thread['thread_id']
        category = json_thread['category']

        if not os.path.exists("Viva_forum/per_category/"+category) :
            os.makedirs("Viva_forum/per_category/"+category)

        title = json_thread['title']

        out = open("Viva_forum/per_category/"+category+"/"+thread_id+".xml","w")
        out.write("<?xml version=\"1.0\"?>\n")
        out.write("<forum type=\"viva\">\n")

        thread = Thread(thread_id,title,category,"")

        htmlcontent = json_thread['content']
        
#        sys.stderr.write(thread_id+"\n")    

        htmlstruct = BSHTML(htmlcontent)
        nrofposts = len(htmlstruct.findAll('span'))
        sys.stderr.write(thread_id+": nr of posts:"+str(nrofposts)+"\n")
        i = 0
        datepattern = re.compile("[0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]")
        while i < nrofposts :
            if datepattern.match(htmlstruct.findAll('span')[i].contents[0].strip()) :
 #               sys.stderr.write(htmlstruct.findAll('span')[i].contents[0].strip()+"\n")
                # 26-01-2015 22:31
                timestamp = htmlstruct.findAll('span')[i].contents[0].strip()
                author = htmlstruct.findAll('strong')[i].contents[0].strip()
                if re.match("anoniem[0-9]+",author) :
                    author = "anoniem"
                content = htmlstruct.findAll('p')[i].contents[0]
                parentid = findQuote(content,thread_id)
                #sys.stderr.write(thread_id+"\t"+timestamp+"\t"+author+"\n")     
                post = Post(str(i),author,timestamp,content,str(parentid))
                thread.addPost(post)
                posts[(author,timestamp)] = i
                postsperthread[thread_id] = posts
            else :
                sys.stderr.write("span item is not a timestamp: "+htmlstruct.findAll('span')[i].contents[0].strip()+" --> removed\n")
                del htmlstruct.findAll('span')[i]
                nrofposts -= nrofposts
                # there was a 'span' item found that was counted as timestamp (new post) but appeared not to be a timestamp. 
                # so no new post here and array of authors is 1 shorter than array of timestamp
            i += 1

        thread.printXML(out)
        thread.printTXT(outtxt)
        out.write("</forum>\n")
        out.close()
    
outtxt.close()

#print("</forum>")

