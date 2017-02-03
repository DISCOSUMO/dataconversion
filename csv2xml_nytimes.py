# coding=utf-8
# python csv2xml_nytimes.py /Users/suzanverberne/Data/FORUM_DATA/NYTimes/comments_study.csv NYtimes/threads


import sys
import csv
import re

csv_file = sys.argv[1]
out_dir = sys.argv[2]

class Thread:

    def __init__(self,threadid,title,category,ttype):
        self.threadid = threadid
        self.title = title
        self.posts = []
        self.category = category
        self.ttype = ttype

    def addPost(self,post):
        self.posts.append(post)

    def getNrOfPosts(self):
        return len(self.posts)

    def printXML(self,out):
        out.write("<thread id=\""+self.threadid+"\">\n<category>"+self.category+"</category>\n<title>"+self.title+"</title>\n<posts>\n")
        for post in self.posts:
            post.printXML(out)
        out.write("</posts>\n</thread>\n")

    def printTXT(self,out):
        for post in self.posts:
            post.printTXT(out)

def clean_up(text):
    clean_text = re.sub(r"\t","",text)
    clean_text = re.sub("[\r\n]"," ",clean_text)
    clean_text = re.sub("<[^>]+>"," ",clean_text)
    clean_text = re.sub("&nbsp;"," ",clean_text)
    clean_text = re.sub("&","&amp;",clean_text)
    clean_text = re.sub("  +"," ",clean_text)
    #print (clean_text)
    return clean_text

class Post:

    def __init__(self,postid,author,timestamp,body,parentid,ups,downs,selected):
        self.postid = postid
        self.author = author
        self.timestamp = timestamp
        self.body = clean_up(body)
        self.parentid = parentid
        self.ups = ups
        self.downs = downs
        self.selected = selected
        #sys.stderr.write(parent_id+" upvotes:"+str(ups)+"\n")

    def printXML(self,out):
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+str(self.timestamp)+"</timestamp>\n<parentid>"+self.parentid+"</parentid>\n<body>"+self.body+"</body>\n<upvotes>"+str(self.ups)+"</upvotes>\n<downvotes>"+str(self.downs)+"</downvotes>\n<selected>"+str(self.selected)+"</selected>\n</post>\n")

    def printTXT(self,out):
        out.write(self.body+"\n")


print("Read ",csv_file)

postcountperthread = dict() # key is threadid, value is # of posts in thread
jsonforlinenr = dict() # key is line number, value is parsed json

#f=open(json_file)
#json_string=f.readline()


urltothreadid = dict()
# dictionary with url as key and threadid as value

threadids = set() # list of thread ids, to find if we have the opening post for a given comment
threads = dict()  # key is threadid, value is Object thread, to find the thread given the thread id
last_threadid_number = 0

with open(csv_file, 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for line in reader:
        #print (line)
        (commentID,commentTitle,commentBody,approveDate,recommendationCount,display_name,location,commentQuestion,commentSequence,status,articleURL,editorsSelection,in_study) = line
        if "http:" in articleURL:
            threadid = ""
            if articleURL in urltothreadid:
                threadid = urltothreadid[articleURL]
            else:
                current_threadid_number = last_threadid_number + 1
                threadid = str(current_threadid_number)
                urltothreadid[articleURL] = threadid
                last_threadid_number = current_threadid_number


with open(csv_file, 'rt',encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for line in reader:
        #print (line)
        (commentID,commentTitle,commentBody,approveDate,recommendationCount,display_name,location,commentQuestion,commentSequence,status,articleURL,editorsSelection,in_study) = line
        #print (commentID)
        if "http:" in articleURL:
            threadid = urltothreadid[articleURL]
            articleURL = re.sub("/$","",articleURL)
            title = articleURL.rsplit('/', 1)[-1]
            title = re.sub("\.html","",title)
            title = re.sub("-"," ",title)
            #print (articleURL,title)
            if title == "":
                print ("warning: empty title!",articleURL,title)
            if threadid in threadids:
                thread = threads[threadid]
            else:
                thread = Thread(threadid,title,"","")
                threads[threadid] = thread
                threadids.add(threadid)


            postid = commentID
            content = commentBody
            timestamp = approveDate
            author = re.sub(r"&",r"&amp;",display_name)
            author = re.sub(r"[^0-9a-zA-Z _@.-]",r"_",author)
            #print (display_name,author)
            ups = recommendationCount
            selected = editorsSelection
            parentid = ""
            post = Post(postid,author,timestamp,content,parentid,ups,0,selected)

            thread.addPost(post)


print ("Print XML output")

for threadid in threadids:
    print(threadid)

    out = open(out_dir+"/"+threadid+".xml","w")
    out.write("<?xml version=\"1.0\"?>\n")
    out.write("<forum type=\"nytimes\">\n")
    thread = threads[threadid]

    thread.printXML(out)
    out.write("</forum>\n")
    out.close()



