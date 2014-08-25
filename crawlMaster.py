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
    self.crawlers = [] # this is mostly here for testing 
    self.results = {}
    self.junk = [] 
    self.frontier = set()
    self.crawlers = [] # for testing 
    self.crawled = [] 
    self.crawlCount = 0
    self.inPort = port
    self.outPort = port +1
    self.finished = threading.Event()   
 
    self.commands = {
    "GTRESULTS":self.getResults,
    "GTURL":self.grantURLs,
    "APPDTO":self.appendTo, 
    "SSTERMS":self.sendSearchTerms } # list of commands mapping Strings to functions
    
    self.lists = {
    "CRAWLED":self.crawled,
    "ERRORS":self.errors,
    "RESULTS":self.results,
    "FRONTIER":self.frontier,
    "REQS":self.req_queue } #remember to update this list    
  
  def checkTime(self):
    #check timestamps on in progress
    pass
  
  def getResults(self,termList):
    # get search terms that we requested 
    addr = termList.pop() 
    for i in range(0,len(termList),2):
        self.results[termList[i]] = int(termList[i+1])

  def grantURLs(self,inList):
    addr = inList.pop()

    if not self.frontier:
      if time.time() - self.startTime > 30:
        self.finished.set() 
      #if the frontier is empty re-append the request to the queue
      self.req_queue.append(["GTURL",addr])
      time.sleep(1)
      return
    
    outList = [] 
    i = 0
    while self.frontier and i < 10: 
      outList.append(self.frontier.pop())      
      i += 1

    self.inProgress += outList # add all the outbound urls to the inProgress list
    self.req("GTURL"+","+",".join(outList),addr,self.outPort)

  def startCrawler(self,crawlerIP):
    self.req("START",crawlerIP,self.outPort)

  def stopCrawler(self,crawlerIP):
    self.req("STOP",crawlerIP,self.outPort)
 
  def startAll(self):
    for ip in self.crawlers:
      self.startCrawler(ip)

  def stopAll(self):
    for ip in self.crawlers:
      self.stopCrawler(ip)

  def appendTo(self,inList):
    #callable over the network, append to a given local list
    addr = inList.pop() # pop the sender's address
    listStr = inList.pop(0)  # pop the list dictionary key
    targetList = self.lists[listStr]    
    
    if listStr == "CRAWLED":
      self.crawlCount += 1 # to compare to how many crawled urls are new
      for url in inList:
        if url in self.inProgress:
           print "out of progress " , url
           self.inProgress.remove(url)

    for url in inList:
      if url not in self.inProgress:   
        if listStr != 'FRONTIER': 
          targetList.append(url)
        elif url not in self.crawled:
          targetList.add(url)
      # the list will need to be filtered for duplicates elsewhere. 
      self.junk.append((listStr,url))   
    if len(self.crawled) >= self.limit: # testing clause 
      self.finished.set()

  def sendSearchTerms(self, arglist):
      #respond to a request for search terms
      crawlerAddr = arglist[0] # pop crawler addr
      if crawlerAddr not in self.crawlers: # and add the crawler to a list 
        self.crawlers.append(crawlerAddr)  # of known crawlers. 

      dictList = []
      for i in self.searchTerms: # deconstruct the dictionary into a string w/commas
        dictList.append(i)
        dictList.append(str(self.searchTerms[i]))
      self.req("GETSTERMS,"+','.join(dictList),crawlerAddr,self.outPort)

  def end(self): # easy testing function 
    self.stopAll()
    endTime = time.time()
    duration =  endTime - self.startTime
    if self.crawlCount:
      successRate = float(len(set(self.crawled)))/self.crawlCount
    else:
      successRate = 0 
    print "Time elapsed: " , duration
    print "number crawled: " , len(self.crawled)
    print "success rate: " , successRate*100 ,"%" 

  @enthread
  def getDone(self):
    self.finished.wait()
    self.end()

  def begin(self, limit=250): # easy testing function
    self.limit = limit
    self.getDone()
    self.startTime = time.time() 
    self.startAll()

class remoteCrawler(commObj):   
  
  def __init__(self,masterIP,masterPort=9013):
    commObj.__init__(self)
    self.searchTerms = {} #dictionary of search terms 
    #self.thread = threading.Thread(target=beginCrawl) # crawler's own personal thread
    self.masterIP = masterIP
    self.outPort = masterPort
    self.inPort = masterPort +1
    #self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #don't forget we might need a socket lock. heh sock-lock
    self.mimes = []
    self.m_list = ['.pdf','.xls']
    self.crawling = False
    self.req_pending = False
    self.errors = [] 
    self.frontier = set()
    self.crawled = []
    self.newLinks = [] 
    self.results = {} # dictionary of urls w/ their score 
    self.finished = threading.Event()
    self.linkDump = set()
    self.linksByPages = [] 

    self.commands = {
    "GETSTERMS":self.getSearchTerms,
    "START":self.startCrawl,
    "STOP":self.stop,
    "GTURL":self.getURLs } # list of commands mapping Strings to functions
    
    self.cache = {} # list of webpage objects
    self.lists = {
    "MIMES":self.mimes,
    "ERRORS":self.errors,
    "LINKS":self.newLinks,
    "RESULTS":self.results}
    

  def crawl(self):
    if not self.frontier: #check if frontier is empty, if so do nothing
      print "empty frontier"
      return 
   
    url = self.frontier.pop() # pop a url from our frontier
    url = url.encode('ascii', 'xmlcharrefreplace') # i'm not sure if this is even 
                                                  #what we want, but it's a temporary fix
                                                  #for the em dash problem

    m_type = mimetypes.guess_type(url,strict=False) #guess the mimetype ==> THIS APPARENTLY  DOESN'T WORK
    
    if m_type[0] or m_type[1]: 
      self.mimes.append(url) # Append the url to the internet media box
      return

    for i in self.m_list: #just to filter for now until a better option is implemented
      if i in url:
        self.mimes.append(url)
        return 
    
    try:
      page = WebPage(url) #try downloading the page!
      page.parse()
      for link in page.internalLinks:
        
        if link != url and link not in self.frontier and link not in self.cache: 
              self.newLinks.append(link)
        
        
      for link in page.externalLinks:
         self.linkDump.add(link)
      
    except Exception as e: #we'll actually handle some errors here one day
      self.errors.append(e)
      return
    
    self.linksByPages.append((url,page.internalLinks[:],page.externalLinks[:]))
    score = self.score(page.plainText)
    self.crawled.append(url)
    if score < 0:
      self.results[url] = score

  def getURLs(self,termList):
    # get the URLs that were sent as per a crawler request 
    # and slap them into our frontier
    addr = termList.pop()
    for i in termList:
      if i and i not in self.frontier:
        self.frontier.add(i)
    self.req_pending = False  

  def getSearchTerms(self,termList):
    # get search terms that we requested 
    addr = termList.pop() 
    for i in range(0,len(termList),2):
        self.searchTerms[termList[i]] = int(termList[i+1])
  
  def cachePage(self,page):
    #update a cache to keep from re-sending common links to the master 
    if page not in self.cache:
      self.cache[page] = 1
    else:
      self.cache[page] += 1 

  def cleanCache(self):
    todel = [] 
    for key in self.cache:
      self.cache[key] -= .5
      if self.cache[key] <= 0: todel.append(key)
    for key in todel:
      del self.cache[key] 

  
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

  def sendResults(self, arglist):
      #generalize this as a send/receive dict funct-pair
      dictList = []
      for i in self.results:
        dictList.append(i)
        dictList.append(str(self.results[i]))
      self.req("GTRESULTS,"+','.join(dictList),self.masterIP,self.outPort)



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
      #Very cursory!!!  
      if self.crawled:
        self.sendList("CRAWLED",self.crawled)
        self.crawled = []

      if self.newLinks:
        for i in range(len(self.newLinks)-1):
          self.cachePage(self.newLinks[i]) # for testing
          self.newLinks[i] = self.newLinks[i].encode('ascii', 'xmlcharrefreplace')
          if self.newLinks[i] in self.frontier:
            self.newLinks.pop(i)
      

        self.sendList("FRONTIER",self.newLinks)
        self.newLinks = []
 
      if self.results:
          self.sendResults(self.results)
          self.results = {}

      if not self.frontier and not self.req_pending:
        self.req("GTURL",self.masterIP,self.outPort)
        self.req_pending = True
      
      self.cleanCache() # also for testing 
      
      if self.frontier:
          print "going to sleep"
          time.sleep(3)
          print "waking up to crawl"
          self.crawl()
          print "done crawling" 

  def stop(self,*args):
    self.crawling = False

