class LogItem(object):

    def __init__(self, timestamp, type, message):

        self.timestamp = timestamp
        self.type = type
        self.message = message

    def toString(self):

        return self.timestamp.strftime('%b %d %H:%M:%S') + "|" + self.type + "|" + self.message