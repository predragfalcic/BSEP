import codecs
import os
import sys
import time
import traceback
import re
from datetime import datetime
import LogItem

def getEvents(logPath):

    with open(logPath) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    LogList = []

    dates = []
    for x in content:
        #match = re.search(r'\d{2}.\d{2}.\d{4}', text)
        dateText = x[:15]
        date = datetime.strptime(dateText, '%b %d %H:%M:%S')
        message = x[15:].strip()
        type = ""
        if ((message.lower().find("critical") != -1) or (message.lower().find("error") != -1)):
            type = "error"
        elif ((message.lower().find("warning") != -1) or (message.lower().find("warn") != -1)):
            type = "warning"
        else:
            type = "info"

        l = LogItem.LogItem(date, message, type)
        LogList.append(l)

    return LogList

def writeToFile(LogList):
    f = open("systemLogs.txt", 'w')
    for x in LogList:
        f.write(x.toString() + "\n")


if __name__ == "__main__":
    #server = None  # None = local machine
    #logTypes = ["System", "Application"]
    LogList = getEvents('/var/log/syslog')
    writeToFile(LogList)
