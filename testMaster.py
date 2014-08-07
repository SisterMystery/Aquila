from crawlMaster import * 

foxM = crawlMaster({"C++":1, "Python": 2, "python":2,"Scala":2,"scala":2})
foxM.listen(foxM.inPort)
foxM.startDQ()
foxM.frontier.append("http://www.internships.com/student")


