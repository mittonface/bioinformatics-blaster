from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('blaster.views',
    url(r'/new/?$', 'add_job', name='add_job'),
    url(r'/view/(?P<job_id>\d+)', 'view_job', name='view_job'),
    url(r'/delete/(?P<job_id>\d+)', 'delete_job', name='delete_job'),
    url(r'$', 'view_jobs', name='view_jobs'),
)
