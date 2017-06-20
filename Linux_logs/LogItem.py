import calendar

class LogItem(object):

    def __init__(self, timestamp, logId, type, compName, message, fileName):

        self.timestamp = timestamp
        self.logId = logId
        self.type = type
        self.compName = compName
        self.message = message
        self.fileName = fileName




    def toString(self):

        return str(self.timestamp) + "|" + self.type + "|" + self.compName + "|" + self.message + "|" + self.fileName