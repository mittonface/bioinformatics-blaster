from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('blaster.views',
    url(r'new/?$', 'add_job', name='add_job'), 
)
