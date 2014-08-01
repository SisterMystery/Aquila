from aquilaUtil import * 
import random, time, mimetypes 



class crawlMaster(object):
  #crawl master over all local and remote threads,
  #spawns local threads and accepts requests via crawler calls to 
  # master methods. Also remote crawlers... later
	def __init__(self,searchDict,port = 9013):
		#self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.searchTerms = searchDict
		self.errors = []
		self.inProgress = [] # list of urls being crawled/read
		self.results = []
		self.frontier = []
		self.crawled = [] 
		self.req_queue = [] #lists with function string followed by arguments  
		self.port = port
		self.commandPort = port +1
		self.commands = {"GTURL":self.grantURLs,"APPDTO":self.appendTo, "SSTERMS":self.sendSearchTerms } # list of commands mapping Strings to functions
		
		self.lists = {"CRAWLED":self.crawled,"ERRORS":self.errors,"RESULTS":self.results,
				"FRONTIER":self.frontier,"REQS":self.req_queue } #remember to update this list		
	
	def checkTime(self):
		#check timestamps on in progress
		pass

	def get(target,listString):
		#connect to target master
		#request a list via liststring
		pass

	def grantURLs(self,crawler):
		pass

	def dequeue(self):
		print "dequeuing"
		msgList = self.req_queue.pop(0)
		try:
			if len(msgList) > 1:
				self.commands[msgList[0]](msgList[1:])
			else:
				self.commands[msgList[0]]()

		except Exception as e:
			print e 
			self.errors.append(e)

	@enthread
	def listen(self):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.bind(('',self.port))
		
		while(1):
			msg = 0
			sock.listen(1)
			conn,addr = sock.accept()
			msg = recv(conn)	
			conn.close()
			if(msg): 
				msg = msg.split(",")
				msg.append(addr)
				self.req_queue.append(msg)


		#queue command and arguments as a tuple in req_queue
	
	
	def stopCrawler(self,crawler):
		pass

	def startCrawler(self,crawler):
		pass
	
	def appendTo(self,listString):
		pass
	
	def sendSearchTerms(self, crawler):
		#send the search term dictionary to the crawler requesting it
		print "THIS PART WORKS"		
		pass
		
"""
	
"""

class remoteCrawler(object):   
  
	def __init__(self,masterIP,masterPort):
		self.searchTerms = {} #dictionary of search terms 
		#self.thread = threading.Thread(target=beginCrawl) # crawler's own personal thread
		self.masterIP = masterIP
		self.port = masterPort
		#self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #don't forget we might need a socket lock. heh sock-lock
		self.mimes = []
		self.errors = [] 
		self.frontier = []
		self.newLinks = [] 
		self.req_queue = []
		self.results = [] # list of urls w/ their score 
		self.commands = {"GETSTERMS":self.getSearchTerms } # list of commands mapping Strings to functions
		self.cache = [] # list of webpage objects
		self.lists = {"MIMES":self.mimes,"ERRORS":self.errors,"LINKS":self.newLinks,"RESULTS":self.results}

	def crawl(self):
		if not self.frontier: #check if frontier is empty, if so do nothing
			print "empty frontier"
			return
		
		url = self.frontier.pop(random.randint(0,len(self.frontier)-1)) #pop a url from our frontier
		m_type = mimetypes.guess_type(url,strict=False) #guess the mimetype to filter out download pages we want to avoid 
		
		if m_type[0] or m_type[1]: 
			self.mimes.append(url) # Append the url to the internet media box
			return
		
		try:
			page = WebPage(url) #try downloading the page!
			page.getLinks() # and ripping some links (+ getContenting "a")
			for link in page.internalLinks:
				if link != url:
							self.newLinks.append(link)
			
		except Exception as e:
			self.errors.append(e)
			return

		try:
			#try to get and score the plaintext
			page.getPlainText() 
			score = self.score(page.PlainText)
			if score > 0:
				self.results.append((url,score))
			return
		
		except:
			try:
				#if that failed just do it with the HTML 
				page.getHTML()
				score =  self.score(page.HTML)
				if score > 0:
					self.results.append((url,score))

				return

			except Exception as e:
				self.errors.append(e)
				return


	def dequeue(self):
		print "dequeuing"
		msgList = self.req_queue.pop(0)
		
		if len(msgList) > 1:
			self.commands[msgList[0]](msgList[1:])
		else:
			self.commands[msgList[0]]()
			
	
	@enthread
	def listen(self):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.bind(('',self.port+1))
		
		while(1):
			
			msg = 0
			sock.listen(1)
			conn,addr = sock.accept()
			msg = recv(conn)	
			conn.close()
			if(msg): 
				msg = msg.split(",")
				self.req_queue.append(msg)			
	
	def getSearchTerms(self,termString):
			terms = termString.split(",")
			for i in range(0,len(terms),2):
				self.searchTerms[terms[i]] = terms[i+1]

	def cachePage(self,page):
		pass 	
	
	def score(self,pageText):
		score = 0
		for term in self.searchTerms:
			if term in pageText:
				score += self.searchTerms[term]
		return score
		
	def req(self,streq):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		#socklock
		sock.connect((self.masterIP,self.port))
		send(sock, streq)
		#data = recv(self.socket)
		sock.close()
		#socklock
		#data = data.split(",")
	  
	def returnList(self,listString):
		pass

	def makeMaster(self):
		#newMaster = crawlMaster(self.searchTerms,self.port)
		# newMaster.get the pertinent stuff
		pass 

	def stop(self):
		pass
#############
# Consider a network comm object of some sort with
# listen, req, etc methods
############
