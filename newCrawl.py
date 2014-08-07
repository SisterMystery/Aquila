from crawlMaster import *

foxC = remoteCrawler('10.10.117.114',9013)
foxC.listen(foxC.inPort)
foxC.startDQ()
foxC.req("SSTERMS",foxC.masterIP,foxC.outPort)
