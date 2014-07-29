from aquilaUtil import * 
import threading, random, time 


class crawlMaster(object):
  #crawl master over all local and remote threads,
  #spawns local threads and accepts requests via crawler calls to 
  # master methods. Also remote crawlers... later
  def __init__(self,searchDict,port = 9013):
    self.searchTerms = searchDict
    self.errors = []
    self.results = []
    self.frontier = []
    self.crawled = [] 
    self.req_queue = []  
    self.port = port
    self.commands = { } # list of commands mapping Strings to functions

  def grantURLs(self,crawler,frontierBit):
    pass
  
  def 

class remoteCrawler(object):   
  
  def __init__(self,masterIP,masterPort):
    self.searchTerms = {} #dictionary of search terms 
    self.thread = threading.Thread(target=beginCrawl) # crawler's own personal thread
    self.masterIP = masterIP
    self.port = masterPort
    self.results = [] # list of urls w/ their score 
    self.commands = { } # list of commands mapping Strings to functions
    self.cache = [] # list of webpage objects

  def crawl(self):
    pass

  def cachePage(self,page):
    pass 

  def requestURLs(self):
    pass
  
  def returnResults(self):
    pass

  def stop(self):
    pass

    
