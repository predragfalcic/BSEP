# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import LogModel

import pickle

import os

from Crypto.Hash import SHA256

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# Create your views here.

def format_date_time_for_db(date_time):
    print date_time
    date_time_splited = date_time.split()
    date_splited = date_time_splited[0].split('/')
    date_time_finished = "20"+date_splited[2]+"-"+date_splited[0]+"-"+date_splited[1] + " " + date_time_splited[1]

    return date_time_finished

@csrf_exempt
def add_log(request):
    data = json.loads(request.body)
    potpis = data['potpis'][-1]
    # print potpis

    if data['System'] == "Linux":
        text = str(data['Date']) + str(data['Type']) + str(data['ComputerName']) \
           + str(data['Message']) + str(data['fajl_logova'])

        public_key = pickle.load(open(os.path.expanduser("/home/student/PycharmProjects/BSEP/Linux_logs/SkladisteLogovaLinux/javniKljuc.p"), "rb"))

    else:
        print "Usao je u else"
        # Text koji se hasuje
        text = str(data['fajl_logova']) + str(data['evt_id']) + str(data['Date']) + \
            str(data['System']) + str(data['Type']) + str(data['Message']) + str(data['ComputerName'])

        public_key = pickle.load( open( os.path.expanduser("~\\Desktop\\Novi Projekat BSEP\\Agent_Win_Logs\\Logovi\\SkladisteLogova\\javniKljuc.p"), "rb" ))
        
    # Hasovanje texta
    hash = SHA256.new(text).digest()
    try:
        # Proveri potpis
        if public_key.verify(hash, data['potpis']):

            final_date = format_date_time_for_db(data['Date'])
            LogModel.objects.create(Log_ident=data['evt_id'], dateTime=final_date,
                                    category=data['Type'], compName=data['ComputerName'],
                                    msg=data['Message'], system=data['System'],
                                    fajl_logova=data['fajl_logova'])
        else:
            print "Kljucevi se ne podudaraju\n"
    except EOFError:
        print "Nema kljuca\n"
    return HttpResponse("Got json data")


