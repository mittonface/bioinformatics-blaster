from django.contrib import admin
from models import MultiFASTAFile, Job, Result, TavernaWorkflow, Input
from models import StoredWorkflows

admin.site.register(MultiFASTAFile)
admin.site.register(Job)
admin.site.register(Result)
admin.site.register(TavernaWorkflow)
admin.site.register(Input)
admin.site.register(StoredWorkflows)
