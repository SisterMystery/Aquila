from crawlMaster import * 

foxM = crawlMaster({"foxes":1, "Torrent": 2,"Glenn":1, "Cencini":1,"Python":2})
foxM.listen(foxM.inPort)
foxM.startDQ()
foxM.frontier.add("http://www.bennington.edu")
foxM.frontier.add("http://www.bennington.edu/Students.aspx")


