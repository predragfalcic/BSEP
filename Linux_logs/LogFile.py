class LogFile(object):

    def __init__(self, name, lastModified):

        self.name = name
        self.lastModified = lastModified

    def toString(self):

        return self.name + "|" + self.lastModified
