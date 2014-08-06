from crawlMaster import * 

foxM = crawlMaster({"Cencini":2, "Python": 1, "python":1})
foxM.listen(foxM.inPort)
foxM.startDQ()
foxM.frontier.append("http://www.bennington.edu/")


