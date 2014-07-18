import requests

tagList = [ "h1", "h2", "h3", "h4", "h5", "h6", "p", "a",
       "article", "body", "code", "embed", "img", "meta"] 
# list of HTML tags that we care about right now

def extract(inString,start,end):
       a = inString.partition(start)
       if a[2]:
               b = a[2].partition(end)
               return([b[0]]+extract(b[2],start,end))
       else:
               return []
  


class WebPage(object): #The object representing a single webpage
  
  def __init__(self,link):
    self.URL = link 
    self.site = self._getSite()
    self.HTTPresponse = requests.get(link) #Hold a requests.response object
                                           # in order to keep all the data 

    self.content = {} #Dictionary to map HTML tag strings to lists of 
                      # corresponding page content       
    self.siteLinks = [] # a list on site links on the webpage
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
        self.siteLinks.append(self.site+link)
  
      


