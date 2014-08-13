from crawlMaster import * 

foxM = crawlMaster({"fox":1, "Torrent": 2, "Cencini":2,"Davis-Goff":2,"Espada":2})
foxM.listen(foxM.inPort)
foxM.startDQ()
foxM.frontier.add("http://www.bennington.edu")


