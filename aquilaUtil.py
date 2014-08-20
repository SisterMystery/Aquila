import requests,time,random,socket,struct,threading,HTMLParser
 

tagList = [ "h1", "h2", "h3", "h4", "h5", "h6", "p", "a",
       "article", "body", "code", "embed", "img", "meta","script"] 
# list of HTML tags that we care about right now

packer = struct.Struct('!L') #packer to pack/unpack data for send/recv functions

startTime = 0

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
		while not self.finished.isSet(): # ? is this even how events work?
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

class WebPageParser(HTMLParser.HTMLParser):
  def __init__(self,webpage):
    HTMLParser.HTMLParser.__init__(self)
    self.tagQueue = [0]
    self.page = webpage    

  def handle_starttag(self,tag,attrs):
    if tag == 'a':
      for attr in attrs:
        if attr[0] == 'href':
          self.page.links.append(attr[1])
    self.tagQueue.append(tag)

  def handle_endtag(self,tag):
    self.tagQueue.pop()

  def handle_data(self,data):
    if self.tagQueue[-1] != 'script':
      self.page.text.append(data)
    if self.tagQueue[-1] not in self.page.content:
      self.page.content[self.tagQueue[-1]] = [data]
    else:
      self.page.content[self.tagQueue[-1]].append(data)

    
class WebPage(object): #The object representing a single webpage
  
  def __init__(self,link):
    self.URL = link 
    self.site = self._getSite() # get the site the page belongs to
    self.HTTPresponse = requests.get(link) #Hold a requests.response object
                                           # in order to keep all the data 
    self.content = {} #Dictionary to map HTML tag strings to lists of 
                        # corresponding page content       
    self.links = []
    self.text = []
    self.parser = WebPageParser(self)
    self.internalLinks = [] # a list on site links on the webpage
    self.onPageLinks = [] # on page links.... 
    self.externalLinks = [] # links to the outside world
  
  def _getSite(self):
    if self.URL.startswith("http://"):
      return("http://"+self.URL.split('/')[2])

    else:
      return(self.URL.split('/')[0])
  
  def parse(self):
    self.getHTML()
    self.parser.feed(self.HTML)
    self.sortLinks()
    self.plainText = reduce(lambda x,y:x+y,self.text)
     
  def sortLinks(self):
    for link in self.links:
      if link.startswith('#'):
        self.onPageLinks.append(link)
      
      elif link.startswith(self.site):
        self.internalLinks.append(link)

      elif link.startswith("http:"):
        self.externalLinks.append(link)

      elif link.startswith('//'):
        self.externalLinks.append("http:"+link)
      
      elif link.startswith('/'):
        self.internalLinks.append(self.site+link)
      
  def getHTML(self):
    self.HTML = self.HTTPresponse.text 

         
