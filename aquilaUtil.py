import requests,time,random,socket,struct,threading 

tagList = [ "h1", "h2", "h3", "h4", "h5", "h6", "p", "a",
       "article", "body", "code", "embed", "img", "meta","script"] 
# list of HTML tags that we care about right now

packer = struct.Struct('!L') #packer to pack/unpack data for send/recv functions

def enthread(func):
		def threadedFunc(*argsLst):
			t = threading.Thread(target=func, args=argsLst)
			t.daemon = True
			t.start()
			return
		return threadedFunc

def recv(connection):
  #receive via Python socket, receives and unpacks "packed" binary data
  msg = ""
  msgLen = packer.unpack(connection.recv(4))[0]
  while len(msg) < msgLen:
     msg += connection.recv(msgLen-len(msg))
  return msg

def send(connection, message):
  #send function, works with receive 
  totalSent = 0
  msgLen = len(message)
  packed_msgLen = packer.pack(msgLen)
  connection.send(packed_msgLen)
  while totalSent < msgLen:
    sent = connection.send(message[totalSent:])
    totalSent += sent

def extract(inString,start,end):
       a = inString.partition(start)
       if a[2]:
               b = a[2].partition(end)
               return([b[0]]+extract(b[2],start,end))
       else:
               return []
  
#class command_req(object): # you know, just a command object to hold command, args, origin
#	def __init__(self,funcString,arglist,originAddr):
		
class commObj(object):
	#class representing one of our network objects
	# has a queue of requests which it dequeues and calls
	def __init__(self):
		self.req_queue = []
	
	@enthread
	def startDQ(self):
		#just for now, will make a real method later
    # loop forever, calling functions in the req_queue
		while 1:
			if self.req_queue:
				self.dequeue()
	
	def dequeue(self):
    #remove things from the req_queue and call them
		msgList = self.req_queue.pop(0) # pop the function name string
		print "dequeuing  " + msgList[0]
		if len(msgList) > 1: # if it has arguments also
     
			self.commands[msgList[0]](msgList[1:]) # call the function by accessing the dictionary
                                            #  that maps strings to functions with the rest
                                            # of the list (list of arguments) as argument
		else:
			self.commands[msgList[0]]()
			
	def req(self,streq,addr,port):
    #make a request to do something
    
		print "sending ==> " +streq 
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.connect((addr,port)) 
		send(sock, streq)
		sock.close()
	
	@enthread
	def listen(self,port):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('',port))
		
		while(1):
			
			msg = 0
			sock.listen(1)
			conn,addr = sock.accept()
			msg = recv(conn)	
			conn.close()
			print "received ==> " + msg 
			if(msg): 
				msg = msg.split(",")
				msg.append(addr[0])
				self.req_queue.append(msg)	

class WebPage(object): #The object representing a single webpage
  
  def __init__(self,link):
    self.URL = link 
    self.site = self._getSite() # get the site the page belongs to
    self.HTTPresponse = requests.get(link) #Hold a requests.response object
                                           # in order to keep all the data 

    self.content = {} #Dictionary to map HTML tag strings to lists of 
                      # corresponding page content       
    self.internalLinks = [] # a list on site links on the webpage
    self.onPageLinks = [] # on page links.... 
    self.externalLinks = [] # links to the outside world
  
  def _getSite(self):
    if self.URL.startswith("http://"):
      return("http://"+self.URL.split('/')[2])

    else:
      return(self.URL.split('/')[0])

  def _extractText(self,tag,inString):
  #Recursive text extraction, returns a list of strings/unicode
  # containing the content of a given HTML tag
         start = "<"+tag
         end = "</"+tag+">"
         a = inString.partition(start)
         if a[2]:
               b = a[2].partition(end)
               return([b[0]]+self._extractText(tag,b[2]))
         else:
               return []

  def getContent(self,tag):
    # Wraps the extractText function and populates self.content
    self.content[tag] = self._extractText(tag,self.HTTPresponse.text)

  def getLinks(self):
    #shove all the links in the correct lists based on their prefixes
    self.getContent("a") 
    linkList = []
    for linkSite in self.content["a"]:
      if 'href="' in linkSite:
        linkList.append(extract(linkSite,'href="','"')[0])  
    for link in linkList:
      if link.startswith('#'):
        self.onPageLinks.append(link)
      
      elif link.startswith("http:"):
        self.externalLinks.append(link)

      elif link.startswith('//'):
        self.externalLinks.append("http:"+link)
      
      elif link.startswith('/'):
        self.internalLinks.append(self.site+link)
  def getHTML(self):
    self.HTML = self.HTTPresponse.text 
 
  def getPlainText(self):
    #fetch all the text that isn't HTML by removing the javascript and 
    #getting everything that isn't in angle brackets
    #more reasonable implementation coming soon
    count = 0
    indexA = []
    indexB = []
    text = self.HTTPresponse.text
    jscript = extract(self.HTTPresponse.text,"<script>","</script>")
    for j in jscript:
      text = text.replace(j,"")
  
    for char in self.HTTPresponse.text:
      if char == "<":
        indexA.append(count)
      if char == ">":
        indexB.append(count+1)
      
      count += 1
    
    for i in xrange(len(indexA)):
      text = text.replace(self.HTTPresponse.text[indexA[i]:indexB[i]],"")
    self.plainText = text


         
