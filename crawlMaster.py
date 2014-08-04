from aquilaUtil import * 
import random, time, mimetypes 



class crawlMaster(commObj):
  #crawl master over all local and remote threads,
  #spawns local threads and accepts requests via crawler calls to 
  # master methods. Also remote crawlers... later
	def __init__(self,searchDict,port = 9013):
		commObj.__init__(self)
		#self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.searchTerms = searchDict
		self.errors = []
		self.inProgress = [] # list of urls being crawled/read
		self.results = []
		self.frontier = []
		self.crawled = [] 
		self.inPort = port
		self.outPort = port +1
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

	def grantURLs(self,inList):
		addr = inList.pop()
		
		outList = []		
		for i in range(5):
			if self.frontier:
				outList.append(self.frontier.pop(random.randint(0,len(self.frontier)-1)))

		self.req("GTURL"+","+",".join(outList),addr,self.outPort)

	def startCrawler(self,crawlerIP):
		self.req("START",crawlerIP,self.outPort)

	def stopCrawler(self,crawlerIP):
		self.req("START",crawlerIP,self.outPort)
	
	def appendTo(self,inList):
		addr = inList.pop()
		targetList = self.lists[inList.pop(0)]		
		for i in inList:
			if i not in targetList:
				targetList.append(i)
					

	def sendSearchTerms(self, arglist):
			crawlerAddr = arglist[0]
			dictList = []
			for i in self.searchTerms:
				dictList.append(i)
				dictList.append(str(self.searchTerms[i]))
			self.req("GETSTERMS,"+','.join(dictList),crawlerAddr,self.outPort)

"""
	
"""

class remoteCrawler(commObj):   
  
	def __init__(self,masterIP,masterPort):
		commObj.__init__(self)
		self.searchTerms = {} #dictionary of search terms 
		#self.thread = threading.Thread(target=beginCrawl) # crawler's own personal thread
		self.masterIP = masterIP
		self.outPort = masterPort
		self.inPort = masterPort +1
		#self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #don't forget we might need a socket lock. heh sock-lock
		self.mimes = []
		self.crawling = False
		self.errors = [] 
		self.frontier = []
		self.newLinks = [] 
		self.results = [] # list of urls w/ their score 
		self.commands = {"GETSTERMS":self.getSearchTerms,"START":self.startCrawl,
			"STOP":self.stop,"GTURL":self.getURLs } # list of commands mapping Strings to functions
		
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


	def getURLs(self,termList):
		addr = termList.pop()
		for i in termList:
			self.frontier.append(i)
	
	def getSearchTerms(self,termList):
		addr = termList.pop()	
		for i in range(0,len(termList),2):
				self.searchTerms[termList[i]] = int(termList[i+1])
	
	@enthread
	def startCrawl(self,*args):
		self.crawling = True
		while self.crawling and len(self.frontier) > 0:
			self.crawl()
		

	def cachePage(self,page):
		pass 	
	
	def score(self,pageText):
		score = 0
		for term in self.searchTerms:
			if term in pageText:
				score += self.searchTerms[term]
		return score
		
	def sendList(self,destList,inList):
		#append to one of the master's lists 
		listString = 'APPDTO'+','+destList+','+','.join(inList) #maybe do the efficiency thing to make this not a "+" op
		self.req(listString,self.masterIP,self.outPort)

	def sendResults(self,dest,toSend):
			dictList = []
			for i in toSend:
				dictList.append(i[0])
				dictList.append(str(i[1]))
			self.sendList(dest,dictList)			

	def makeMaster(self):
		#newMaster = crawlMaster(self.searchTerms,self.port)
		# newMaster.get the pertinent stuff
		pass 

	@enthread #enthreaded for testing purposes
	def startCrawl(self,*args):
		self.crawling = True
		print "starting the crawl"
		while self.crawling:
			 
			#cursory startCrawl
			

			if self.newLinks:
				self.sendList("FRONTIER",self.newLinks)
				self.newLinks = [] 
			if self.results:
					self.sendResults("RESULTS",self.results)
					self.results = [] 
			if len(self.frontier) < 1:
				self.req("GTURL",self.masterIP,self.outPort)

		
			if self.frontier:
					print "going to sleep"
					time.sleep(5)
					print "waking up to crawl"
					self.crawl()
					print "done crawling"	

	def stop(self,*args):
		self.crawling = False

