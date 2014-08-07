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
    self.frontier = []
    self.crawlers = [] # for testing 
    self.crawled = [] 
    self.inPort = port
    self.outPort = port +1
    self.commands = {"GTRESULTS":self.getResults,"GTURL":self.grantURLs,"APPDTO":self.appendTo, "SSTERMS":self.sendSearchTerms } # list of commands mapping Strings to functions
    
    self.lists = {"CRAWLED":self.crawled,"ERRORS":self.errors,"RESULTS":self.results,
        "FRONTIER":self.frontier,"REQS":self.req_queue } #remember to update this list    
  
  def checkTime(self):
    #check timestamps on in progress
    pass
  
  def getResults(self,termList):
    # get search terms that we requested 
    addr = termList.pop() 
    for i in range(0,len(termList),2):
        self.results[termList[i]] = int(termList[i+1])

  def grantURLs(self,inList):
    #respond to a request from a crawler with urls
    addr = inList.pop() 
    
    outList = []    
    for i in range(len(self.frontier)/3+1): 
      #five times (for now) pop a random url from the frontier to send
      if self.frontier:
        outList.append(self.frontier.pop(random.randint(0,len(self.frontier)-1)))
      else:
        return
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
    addr = inList.pop() # pop the string key of the list to append to
    targetList = self.lists[inList.pop(0)]    
    for i in inList:
      if i not in targetList and i not in self.crawled:
        targetList.append(i)
          

  def sendSearchTerms(self, arglist):
      #respond to a request for search terms
      crawlerAddr = arglist[0]
      
      if crawlerAddr not in self.crawlers:
        self.crawlers.append(crawlerAddr)

      dictList = []
      for i in self.searchTerms:
        dictList.append(i)
        dictList.append(str(self.searchTerms[i]))
      self.req("GETSTERMS,"+','.join(dictList),crawlerAddr,self.outPort)


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
    self.m_list = ['.pdf','.xls']
    self.crawling = False
    self.errors = [] 
    self.frontier = []
    self.crawled = []
    self.newLinks = [] 
    self.results = {} # dictionary of urls w/ their score 
    self.commands = {"GETSTERMS":self.getSearchTerms,"START":self.startCrawl,
      "STOP":self.stop,"GTURL":self.getURLs } # list of commands mapping Strings to functions
    
    self.cache = [] # list of webpage objects
    self.lists = {"MIMES":self.mimes,"ERRORS":self.errors,"LINKS":self.newLinks,"RESULTS":self.results}
    

  def crawl(self):
  
    if not self.frontier: #check if frontier is empty, if so do nothing
      print "empty frontier"
      return 
   
    url = self.frontier.pop(random.randint(0,len(self.frontier)-1)) #pop a url from our frontier
    url = url.encode('ascii', 'xmlcharrefreplace') # i'm not sure if this is even what we want, but it's a temporary fix for the em dash problem
    m_type = mimetypes.guess_type(url,strict=False) #guess the mimetype ==> THIS DOESN'T WORK
    
    if m_type[0] or m_type[1]: 
      self.mimes.append(url) # Append the url to the internet media box
      return
    #just to filter for now until a better option is implemented
    for i in self.m_list:
      if i in url:
        self.mimes.append(url)
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
      self.crawled.append(url)
      if score > 0:
        self.results.append((url,score))
      return
    
    except:
      try:
        #if that failed just do it with the HTML 
        page.getHTML()
        score =  self.score(page.HTML)
        self.crawled.append(url)
        if score > 0:
          self.results.append((url,score))

        return

      except Exception as e:
        self.errors.append(e)
        return


  def getURLs(self,termList):
    # get the URLs that were sent as per a crawler request 
    # and slap them into our frontier
    addr = termList.pop()
    for i in termList:
      if i:
        self.frontier.append(i)
  
  def getSearchTerms(self,termList):
    # get search terms that we requested 
    addr = termList.pop() 
    for i in range(0,len(termList),2):
        self.searchTerms[termList[i]] = int(termList[i+1])
  
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

  def sendResults(self, arglist):
      #generalize this as a send/receive dict funct-pair
      dictList = []
      for i in self.results:
        dictList.append(i)
        dictList.append(str(self.searchTerms[i]))
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
      if len(self.crawled) > 20:
        self.sendList("CRAWLED",self.crawled)
        self.crawled = []
      if self.newLinks:
        for i in range(len(self.newLinks)-1):
          self.newLinks[i] = self.newLinks[i].encode('ascii', 'xmlcharrefreplace')
        self.sendList("FRONTIER",self.newLinks)
        self.newLinks = []
 
      if self.results:
          self.sendResults(self.results)
          self.results = [] 
      if len(self.frontier) < 3:
        self.req("GTURL",self.masterIP,self.outPort)
        time.sleep(4)
    
      if self.frontier:
          print "going to sleep"
          time.sleep(5)
          print "waking up to crawl"
          self.crawl()
          print "done crawling" 

  def stop(self,*args):
    self.crawling = False

