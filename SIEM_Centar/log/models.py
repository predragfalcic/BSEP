# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class LogModel(models.Model):
    Log_ident = models.CharField(max_length = 150)
    compName = models.CharField(max_length = 100)
    category = models.CharField(max_length = 30)
    msg = models.TextField(max_length = 200)
    dateTime = models.DateTimeField()
    system = models.CharField(max_length = 30, default="Unknown")
    
