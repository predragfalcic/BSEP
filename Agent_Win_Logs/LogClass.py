class LogItem(object):
    """
    Atributi klase LogItem mogu da se
    menjaju u zavisnosti od toga koji su nam potrebni.
    """
    def __init__(self, dateTime, logId, compName, category, fajl, msg=None):
        self.dateTime = dateTime
        self.logId = logId
        self.compName = compName
        self.category = category
        self.msg = msg
        # fajl predstavlja iz kog fajla su logovi procitani
        # to jest da li su procitani iz sistemski logovi ili security ili aplikacioni logovi
        self.fajl = fajl

    def toFile(self):
        return self.dateTime+"|"+self.logId+"|"+self.compName+"|"+self.category+"|"+self.fajl


