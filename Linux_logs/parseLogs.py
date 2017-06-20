import codecs
import new
import os
import sys
import traceback
import re
import string
from datetime import datetime
import LogItem
import time
import socket
import requests
from requests.exceptions import ConnectionError
import json
import platform

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

import pickle
import calendar


def zakucajDatum(datum):
    #stringTimeStamp = datum.strftime('%b %d %H:%M:%S')
    splitted = datum.split()
    splitted2 = splitted[0].split("-")
    print "aaa" + splitted2[0] + "|" + splitted2[1] + "|" + splitted2[2]
    #dict1 = dict((v, k) for k, v in enumerate(calendar.month_abbr))
    # print dict1
    #splitted[0] == "Jan"
    # mesec = "01";
    # if (splitted[0] == "Jan"):
    #     mesec = "01"
    # elif (splitted[1] == "Feb"):
    #     mesec = "02"
    string2 = splitted2[1] + "/" + splitted2[2] + "/" + "17" + " " + splitted[1]
    return string2

def nabaviSveLogoveIkad():
    logTypes = ["System", "Security"]
    putanje = ['/var/log/syslog', '/var/log/auth.log']
    LogListSystem = getEvents('/var/log/syslog')
    writeToFile1(LogListSystem, "systemLogs.txt")
    LogListSecurity = getEvents('/var/log/auth.log')
    writeToFile1(LogListSecurity, "securityLogs.txt")

    lista = []

    m1 = {'logType' : logTypes[0], 'list' : LogListSystem}
    m2 = {'logType' : logTypes[1], 'list' : LogListSecurity}

    lista.append(m1)
    lista.append(m2)

    return lista

def getEvents(logPath):

    with open(logPath) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    LogList = []
    f.close()

    dates = []
    for x in content:
        """dateText = x[:15]
        date = datetime.strptime(dateText, '%b %d %H:%M:%S')
        message = x[15:].strip()"""

        splittedX = x.split()
        dateText = splittedX[0]+" "+splittedX[1]+" "+splittedX[2]
        date = datetime.strptime(dateText, '%b %d %H:%M:%S')
        compName = splittedX[3]
        message = " ".join(splittedX[4:])

        type = ""
        if ((message.lower().find("critical") != -1) or (message.lower().find("error") != -1)):
            type = "error"
        elif ((message.lower().find("warning") != -1) or (message.lower().find("warn") != -1)):
            type = "warning"
        else:
            type = "info"


        l = LogItem.LogItem(date, "", type, compName, message, logPath)
        LogList.append(l)

    return LogList

def writeToFile1(LogList, file):
    f = open(file, 'w')
    for x in LogList:
        f.write(x.toString() + "\n")

# Upisujemo poslednji log u fajl
# postoje dva fajla, za sistemske i security logove
def writeToFile(fileName, log, log_type):
    f = open(fileName + "/" + log_type +".txt", 'w')
    f.write(log.toString())


def readFile(fileName):
    l = None
    with open(fileName) as f:
        content = f.readlines()
        for line in content:
            if len(line) > 0:
                splited_log = line.split("|")

                for i in splited_log:
                    l = LogItem.LogItem(splited_log[0], "*", splited_log[1], splited_log[2], splited_log[3], splited_log[4])

    return l

if __name__ == "__main__":
    #server = None  # None = local machine
    # logTypes = ["System", "Security"]
    # LogListSystem = getEvents('/var/log/syslog')
    # writeToFile(LogListSystem, "systemLogs.txt")
    # LogListSecurity = getEvents('/var/log/auth.log')
    # writeToFile(LogListSecurity, "securityLogs.txt")
    #LogListApplication = getEvents('/var/log/syslog')
    #writeToFile(LogListApplication, "applicationLogs.txt")

    listaLogova = []
    lista = []
    URL = "http://localhost:8000/log/add/"

    server = None  # None = local machine
    logTypes = ["System", "Security"]

    key = " "
    public_key = " "
    try:
        print "caocaocaocaocaocoacoacaco"
        # Ucitaj kljuceve iz fajla
        key = pickle.load( open( "SkladisteLogovaLinux/privateKey.p", "rb" ) )
        public_key = pickle.load( open( "SkladisteLogovaLinux/javniKljuc.p", "rb" ) )
    except EOFError:
        print "Nema kljuceva\n"

    # Ukoliko ne postoje kljucevi kreiraj nove
    if key is " " and public_key is " ":
        print "Kljucevi ne postoje, generisem nove\n"
        # Generisi private i public key
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        public_key = key.publickey()

        # Upisujemo kljuc u fajl
        pickle.dump( key, open( "SkladisteLogovaLinux/privateKey.p", "wb" ) )
        # Upisujemo javni kljuc u fajl
        pickle.dump( public_key, open( "SkladisteLogovaLinux/javniKljuc.p", "wb" ) )


    while True:
        lista = nabaviSveLogoveIkad()
        for i in lista:

            print "Provera " + i['logType'] + " Logova\n"

            fajl = "SkladisteLogovaLinux"

            poslednji_log = None
            try:
                print "citaj iz fajla"
                poslednji_log = readFile(fajl    + "/" + i['logType'] + ".txt")
                #print "poslednji log " + poslednji_log.timestamp
            except IOError as e:
                print(os.strerror(e.errno))

            if poslednji_log != None:
                print "Log je procitan iz fajla\n"
                print poslednji_log
            else:
                print "Log je None, preuzima se poslednji log iz liste logova\n"
                print "Salje se na server\n"
                poslednji_log = i['list'][-1]
                if "warning" in poslednji_log.type:
                    logType = "warning"
                elif "error" in poslednji_log.type:
                    logType = "error"
                else:
                    logType = "info"
                datum = zakucajDatum(str(poslednji_log.timestamp))
                # Text koji se hasuje
                text = str(datum) + str(poslednji_log.type)  + str(poslednji_log.compName) \
                       + str(poslednji_log.message) + str(poslednji_log.fileName)
                # Hasovanje texta
                hash = SHA256.new(text).digest()
                # Potpisivanje hasha
                signature = key.sign(hash, '')

                # jsonData = {'fajl_logova': str(poslednji_log.fileName), 'evt_id': "*", 'Date': str(poslednji_log.timestamp),
                #             'System': platform.system(), 'Type': poslednji_log.type, 'Message': poslednji_log.message,
                #             'ComputerName': poslednji_log.compName}
                print "Ovo je datum 1 " + datum
                jsonData = {'fajl_logova': str(poslednji_log.fileName), 'evt_id': "*", 'Date': datum,
                            'System': platform.system(), 'Type': poslednji_log.type, 'Message': poslednji_log.message,
                            'ComputerName': poslednji_log.compName}

                jsonData['potpis'] = signature

                print json.dumps(jsonData)
                # print "Proveran potpis " + str(public_key.verify(hash, signature))
                time.sleep(3)

                try:
                    r = requests.post(URL, data=json.dumps(jsonData))
                except ConnectionError as e:
                    print e

                # poslednji_log = novi_poslednji_log

                fajl = "SkladisteLogovaLinux"

                writeToFile(fajl, poslednji_log, i['logType'])
            # print poslednji_log

            novi_poslednji_log = i['list'][-1]
            print poslednji_log.timestamp
            print novi_poslednji_log.timestamp
            if set(str(poslednji_log.timestamp).split(' ')) == set(str(novi_poslednji_log.timestamp).split(' ')):
                print "NEMA NOVIH LOGOVA"

                poslednji_log = novi_poslednji_log

                fajl = "SkladisteLogovaLinux"

                writeToFile(fajl, poslednji_log, i['logType'])

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

                if "warning" in novi_poslednji_log.type:
                    logType = "warning"
                elif "error" in novi_poslednji_log.type or "Error" in novi_poslednji_log.type:
                    logType = "error"
                else:
                    logType = "info"

                # Text koji se hasuje
                datum = zakucajDatum(str(novi_poslednji_log.timestamp))
                text = str(datum) + str(novi_poslednji_log.type)  + str(novi_poslednji_log.compName) \
                       + str(novi_poslednji_log.message) + str(novi_poslednji_log.fileName)
                # Hasovanje texta
                hash = SHA256.new(text).digest()
                # Potpisivanje hasha
                signature = key.sign(hash, '')

                datum = zakucajDatum(str(novi_poslednji_log.timestamp))
                #print "Ovo je datum 2 " + datum
                jsonData = {'fajl_logova': str(novi_poslednji_log.fileName), 'evt_id': "*", 'Date': datum,
                            'System': platform.system(), 'Type': novi_poslednji_log.type, 'Message': novi_poslednji_log.message,
                            'ComputerName': novi_poslednji_log.compName}

                jsonData['potpis'] = signature

                print json.dumps(jsonData)
                # print public_key.verify(hash, signature)


                try:
                    r = requests.post(URL, data=json.dumps(jsonData))
                except ConnectionError as e:
                    print e

                poslednji_log = novi_poslednji_log

                fajl = "SkladisteLogovaLinux"

                writeToFile(fajl, poslednji_log, i['logType'])

        time.sleep(20)


