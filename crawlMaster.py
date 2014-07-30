from aquilaUtil import * 
import threading, random, time, mimetypes 


class crawlMaster(object):
  #crawl master over all local and remote threads,
  #spawns local threads and accepts requests via crawler calls to 
  # master methods. Also remote crawlers... later
	def __init__(self,searchDict,port = 9013):
		self.searchTerms = searchDict
		self.errors = []
		self.inProgress = [] # list of urls being crawled/read
		self.results = []
		self.frontier = []
		self.crawled = [] 
		self.req_queue = []  
		self.port = port
		self.commands = { } # list of commands mapping Strings to functions
		self.lists = {"CRAWLED":self.crawled,"ERRORS":self.errors,"RESULTS":self.results,
				"FRONTIER":self.frontier,"REQS":self.req_queue } #remember to update this list

	def checkTime(self):
		#check timestamps on in progress
		pass

	def get(target,listString):
		#connect to target master
		#request a list via liststring
		pass

	def grantURLs(self,crawler,frontierBit):
		pass
  
	def listen(self):
		#queue command and arguments as a tuple in req_queue
		pass
	
	def stopCrawler(self,crawler):
		pass

	def startCrawler(self,crawler):
		pass
	
	def appendTo(self,listString):
		pass
	
	def sendSearchTerms(self, crawler):
		pass
		
"""
	
"""

class remoteCrawler(object):   
  
	def __init__(self,masterIP,masterPort):
		self.searchTerms = {} #dictionary of search terms 
		#self.thread = threading.Thread(target=beginCrawl) # crawler's own personal thread
		self.masterIP = masterIP
		self.port = masterPort
		self.mimes = []
		self.errors = [] 
		self.frontier = []
		self.newLinks = [] 
		self.results = [] # list of urls w/ their score 
		self.commands = { } # list of commands mapping Strings to functions
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
		
		
	
	def cachePage(self,page):
		pass 	
	
	def score(self,pageText):
		score = 0
		for term in self.searchTerms:
			if term in pageText:
				score += self.searchTerms[term]
		return score
		

	def requestURLs(self):
		pass
  
	def returnList(self,listString):
		pass

	def makeMaster(self):
		#newMaster = crawlMaster(self.searchTerms,self.port)
		# newMaster.get the pertinent stuff
		pass 

	def stop(self):
		pass

"""
fox = remoteCrawler('',9013)
fox.searchTerms["red"] = 5
fox.frontier.append("http://en.wikipedia.org/wiki/Random")
fox.crawl()
 """
