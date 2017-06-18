class LogItem(object):
    """
    Atributi klase LogItem mogu da se
    menjaju u zavisnosti od toga koji su nam potrebni.
    """
    def __init__(self, dateTime, logId, compName, category, msg):
        self.dateTime = dateTime
        self.logId = logId
        self.compName = compName
        self.category = category
        self.msg = msg


