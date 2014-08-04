from crawlMaster import * 

foxM = crawlMaster({"red":1, "blue": 5, "yellow":2})
foxM.listen(foxM.inPort)
foxM.startDQ()
foxM.frontier.append("http://www.bennington.edu/")


