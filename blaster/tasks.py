from celery import Celery
from models import TavernaWorkflow, Output
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
    status_url = "http://162.243.48.240:8080/tavernaserver/rest/runs/%s/status" % (workflow.uuid)

    b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS)).replace('\n', '')

    headers = {
        "Authorization": "Basic %s" % (b64),
    }

    req = urllib2.Request(status_url, None, headers)

    try:
        response = urllib2.urlopen(req)
    except urllib2.URLError:
        # most probably the tomcat server went down. It will be back soon.
        # delay a bit and then run the task again
        time.sleep(10)
        monitor_workflow.delay(workflow_id)
    else:
        val = response.read()

        if val == "Initialized":
            workflow.status = 'Running'
            workflow.start()
            time.sleep(5)
            monitor_workflow.delay(workflow_id)
        elif val == "Operating":
            time.sleep(10)
            monitor_workflow.delay(workflow_id)
        elif val == "Finished":
            workflow.status = 'Complete'
            workflow.save()

            # create links to the outputs
            make_outputs(workflow)
        elif val == "Failed":
            workflow.status = 'Failed'
            workflow.save()

def make_outputs(w):
    # Since I need this finished by tomorrow, I'm just going to do some
    # faith based programming and assume that all of the outputs are created
    # on a success
    base_url = "http://162.243.48.240:8080/tavernaserver/rest/runs/%s/wd/out/" % (w.uuid)

    GRAPHIC = "getResult_graphic_output"
    ORIGINAL = "getResult_original_output"
    ID_LIST = "getResult_IDList"

    # graphic output
    o1 = Output(type="graphic", link=base_url+GRAPHIC, workflow=w)
    o1.save()

    o2 = Output(type="similar", link=base_url+ID_LIST, workflow=w)
    o2.save()

    o3 = Output(type="text", link=base_url+ORIGINAL, workflow=w)
    o3.save()

