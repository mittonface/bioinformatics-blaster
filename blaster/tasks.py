from celery import Celery
from models import TavernaWorkflow
from django.conf import settings
import time
import base64
import urllib2

app = Celery('tasks', broker="django://")
TAVERNA_USER = getattr(settings, "TAVERNA_USER", None)
TAVERNA_PASS = getattr(settings, "TAVERNA_PASS", None)


@app.task
def monitor_workflow(workflow_id):
    workflow = TavernaWorkflow.objects.get(pk=workflow_id)
    status_url = "http://107.170.42.52:8080/taverna/rest/runs/%s/status" % (workflow.uuid)

    b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS)).replace('\n', '')

    headers = {
        "Authorization": "Basic %s" % (b64),
    }

    req = urllib2.Request(status_url, None, headers)
    response = urllib2.urlopen(req)

    val = response.read()

    if val == "Initialized":
        workflow.status = 'R'
        workflow.start()
        time.sleep(5)
        monitor_workflow.delay(workflow_id)
    elif val == "Operating":
        time.sleep(10)
        monitor_workflow.delay(workflow_id)
    elif val == "Finished":
        workflow.status = 'C'
        workflow.save()
    elif val == "Failed":
        workflow.status = 'F'
        workflow.save()


