# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import LogModel

# Register your models here.
class LogAdmin(admin.ModelAdmin):
    list_display = ('Log_ident', 'compName', 'category', 'fajl_logova', 'system', 'dateTime')
    search_fields = ('Log_ident', 'msg')
    list_filter =('Log_ident', 'compName', 'category', 'system', 'fajl_logova')
admin.site.register(LogModel, LogAdmin)
