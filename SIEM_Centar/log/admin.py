# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import LogModel

# Register your models here.
class LogAdmin(admin.ModelAdmin):
    pass

admin.site.register(LogModel, LogAdmin)
