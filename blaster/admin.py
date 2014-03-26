from django.contrib import admin
from models import ABIFile, FASTAFile, Job, Result, TavernaWorkflow, Input

admin.site.register(ABIFile)
admin.site.register(FASTAFile)
admin.site.register(Job)
admin.site.register(Result)
admin.site.register(TavernaWorkflow)
admin.site.register(Input)
