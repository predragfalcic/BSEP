import codecs
import new
import os
import sys
import time
import traceback
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import string
import re
from LogClass import LogItem
import time
import socket
import requests
from requests.exceptions import ConnectionError
import json
import platform

reload(sys)
sys.setdefaultencoding('utf-8')

# ----------------------------------------------------------------------
def getAllEvents(server, logtypes, basePath):
    """
    """
    
    lista = []
    print "usao je ovde"
    if not server:
        serverName = "localhost"
    else:
        serverName = server
    for logtype in logtypes:
        listaLogova = []
        path = os.path.join(basePath, "%s_%s_log.log" % (serverName, logtype))
        listaLogova = getEventLogs(server, logtype, path, logtype)
        mapa = {}
        mapa['log_type'] = logtype
        mapa['list'] = listaLogova
        lista.append(mapa)
        print "----------------------------------"
    return lista


def date2sec(evt_date):
    '''
    Ova funkcija konvertuje datum u formatu
    '12/23/99 15:54:09' u sekunde.
    '''
    regexp = re.compile('(.*)\\s(.*)')  # store result in site
    reg_result = regexp.search(evt_date)
    date = reg_result.group(1)
    the_time = reg_result.group(2)
    (mon, day, yr) = map(lambda x: string.atoi(x), string.split(date, '/'))
    (hr, min, sec) = map(lambda x: string.atoi(x), string.split(the_time, ':'))
    tup = [yr, mon, day, hr, min, sec, 0, 0, 0]

    sec = time.mktime(tup)

    return sec

# Upisujemo poslednji log u fajl
# postoje dva fajla, za sistemske i security logove
def writeToFile(fileName, log, log_type):
    f = open(fileName + "\\" + log_type +".txt", 'w')
    f.write(log.toFile())
        
# ----------------------------------------------------------------------
def getEventLogs(server, logtype, logPath, fajl):
    """
    Get the event logs from the specified machine according to the
    logtype (Example: Application) and save it to the appropriately
    named log file
    """
    print "Logging %s events" % logtype
    log = codecs.open(logPath, encoding='utf-8', mode='w')
    line_break = '-' * 20
    print server
    log.write("\n %s Log of %s Events \n" % (server, logtype))
    log.write(line_break)
    log.write("\n Created: %s\n\n" % time.ctime())
    log.write(line_break)
    log.write("\n" + line_break + "\n")
    hand = win32evtlog.OpenEventLog(server, logtype)
    total = win32evtlog.GetNumberOfEventLogRecords(hand)
    print "Total events in %s = %s" % (logtype, total)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand, flags, 0)
    evt_dict = {win32con.EVENTLOG_AUDIT_FAILURE: 'EVENTLOG_AUDIT_FAILURE',
                win32con.EVENTLOG_AUDIT_SUCCESS: 'EVENTLOG_AUDIT_SUCCESS',
                win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
                win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
                win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}

    try:
        events = 1
        logList = []
        begin_sec = time.time()

        while events:
            events = win32evtlog.ReadEventLog(hand, flags, 0)

            for ev_obj in events:
                # samo logovi koji nisu stariji od 8 sati

                the_time = ev_obj.TimeGenerated.Format()  # '12/23/99 15:54:09'
                
                seconds = date2sec(the_time)
                if seconds < begin_sec - 28800: break

                evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))
                computer = str(ev_obj.ComputerName)
                cat = str(ev_obj.EventCategory)
                record = ev_obj.RecordNumber
                msg = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))
                source = str(ev_obj.SourceName)

                if not ev_obj.EventType in evt_dict.keys():
                    evt_type = "unknown"
                else:
                    evt_type = str(evt_dict[ev_obj.EventType])
                
                log.write("\nEvent Date/Time:  %s\n" % the_time)
                log.write("\nEvent ID / Type:  %s / %s\n" % (evt_id, evt_type))
                log.write("\nRecord #%s\n" % record)
                log.write("\nSource: %s\n\n" % source)
                log.write(msg)
                log.write("\n\n")
                log.write(line_break)
                log.write("\n\n")

                #stampanje logova i svih njihovih informacija
                # print string.join((the_time,computer,cat,evt_id,evt_type,msg[0:25]), ' : ')

                #lista sa objektima Logitem klase
                l = LogItem(the_time, evt_id, computer, cat, fajl, msg)
                logList.append(l)


        return logList
    except:
        print traceback.print_exc(sys.exc_info())

    print "Kreiranje logova zavrseno. Lokacija smestanja logova je: %s" % logPath
    
def readFile(fileName):
    l = None
    with open(fileName) as f:
        content = f.readlines()
        for line in content:
            if len(line) > 0:
                splited_log = line.split("|")
                
                for i in splited_log:
                    l = LogItem(splited_log[0], splited_log[1], splited_log[2], splited_log[3], splited_log[4])

    return l
        

if __name__ == "__main__":
    listaLogova = []
    lista = []
    URL = "http://localhost:8000/log/add/"
    
    server = None  # None = local machine
    logTypes = ["System", "Security", "Application"]
    while True:
        lista = getAllEvents(server, logTypes, "Logovi\SkladisteLogova")
        for i in lista:
            
            print "Provera " + i['log_type'] + " Logova\n"

            fajl = "Logovi\SkladisteLogova"
            
            poslednji_log = None
            try:
                poslednji_log = readFile(fajl + "\\" + i['log_type'] +".txt")
            except IOError as e:
                print(os.strerror(e.errno))
                
            if poslednji_log != None:
                print "Log je procitan iz fajla\n" 
                print poslednji_log
            else:
                print "Log je None, preuzima se poslednji log iz liste logova\n"
                poslednji_log = i['list'][-1]

            #print poslednji_log
            
            novi_poslednji_log = i['list'][-1]
            if set(str(poslednji_log.dateTime).split(' ')) == set(str(novi_poslednji_log.dateTime).split(' ')):
                print "NEMA NOVIH LOGOVA"

                poslednji_log = novi_poslednji_log

                fajl = "Logovi\SkladisteLogova"
                
                writeToFile(fajl, poslednji_log, i['log_type'])


                # Ovo dole otkomentarisati ukoliko je baza podataka prazna,
                # Cisto da bi se dodao koji log u nju, da bi mogli pokazati da se logovi uspesno upisuju
                """if "WARNING" in novi_poslednji_log.category:
                    logType = "WARNING"
                elif "CRITICAL" in novi_poslednji_log.category:
                    logType = "CRITICAL"
                elif "ERROR" in novi_poslednji_log.category or "Error" in novi_poslednji_log.category:
                    logType = "ERROR"
                else:
                    logType = "INFO"

                jsonData = {'fajl_logova': i['log_type'], 'evt_id': novi_poslednji_log.logId, 'Date':novi_poslednji_log.dateTime,'System':platform.system(),'Type':logType,'Message':novi_poslednji_log.msg,'ComputerName':socket.gethostname()}

                print json.dumps(jsonData)
                        
                try:
                    r = requests.post(URL, data=json.dumps(jsonData))
                except ConnectionError as e:
                    print e

                poslednji_log = novi_poslednji_log

                fajl = "C:\Users\Privat\Desktop\Logovi\SkladisteLogova"
                
                writeToFile(fajl, poslednji_log, i['log_type'])"""
                
            else:
                print "NOVI LOG. SALJI GA SERVERU"

                if "WARNING" in novi_poslednji_log.category:
                    logType = "WARNING"
                elif "CRITICAL" in novi_poslednji_log.category:
                    logType = "CRITICAL"
                elif "ERROR" in novi_poslednji_log.category or "Error" in novi_poslednji_log.category:
                    logType = "ERROR"
                else:
                    logType = "INFO"

                jsonData = {'fajl_logova': i['log_type'], 'evt_id': novi_poslednji_log.logId, 'Date':novi_poslednji_log.dateTime,'System':platform.system(),'Type':logType,'Message':novi_poslednji_log.msg,'ComputerName':socket.gethostname()}

                print json.dumps(jsonData)
                        
                try:
                    r = requests.post(URL, data=json.dumps(jsonData))
                except ConnectionError as e:
                    print e

                poslednji_log = novi_poslednji_log

                fajl = "Logovi\SkladisteLogova"
                
                writeToFile(fajl, poslednji_log, i['log_type'])
                            
        time.sleep(20)




















