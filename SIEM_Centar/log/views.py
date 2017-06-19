# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import LogModel

# Create your views here.

def format_date_time_for_db(date_time):
    date_time_splited = date_time.split()
    date_splited = date_time_splited[0].split('/')
    date_time_finished = "20"+date_splited[2]+"-"+date_splited[0]+"-"+date_splited[1] + " " + date_time_splited[1]
    return date_time_finished

@csrf_exempt
def add_log(request):
    data = json.loads(request.body)
    print data
    final_date = format_date_time_for_db(data['Date'])
    LogModel.objects.create(Log_ident=data['evt_id'], dateTime=final_date,
                            category=data['Type'], compName=data['ComputerName'],
                            msg=data['Message'], system=data['System'],
                            fajl_logova=data['fajl_logova'])
    return HttpResponse("Got json data")


