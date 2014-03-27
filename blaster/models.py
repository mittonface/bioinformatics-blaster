from django.db import models
from django.conf import settings
import urllib2
import httplib
import base64

STATUS_CHOICES = (
    ("C", "Complete"),
    ("R", "Running"),
    ("F", "Failed"),
)

TAVERNA_USER = getattr(settings, "TAVERNA_USER", None)
TAVERNA_PASS = getattr(settings, "TAVERNA_PASS", None)

class Job(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField(auto_now=True)
    status = models.CharField(max_length=1,
                              choices = STATUS_CHOICES,
                              default = "R")


# An ABI file that may have been uploaded.
# We should be able to parse some information out of it, but for now I'll
# just store the file.
class ABIFile(models.Model):
    path = models.CharField(max_length=300)
    job = models.ForeignKey(Job)

# FASTA files may come from ABI files or be uploaded directly. In the first 
# case we will want to create a link to the parent ABI File. FASTA files will
# be the primary type of object we're operating on. So results will link back
# to fastas
class FASTAFile(models.Model):
    path = models.CharField(max_length=300)
    ABIFile = models.ForeignKey(ABIFile, blank=True, null=True)
    job = models.ForeignKey(Job)


class Result(models.Model):
    fasta = models.ForeignKey(FASTAFile)
    text = models.CharField(max_length=50) # I want to see what I'm working
                                           # with before i expand on this


# This probably doesnt need to be a django model, but I think it's helpful to
# me if I can manage them here
class TavernaWorkflow(models.Model):
    t2flow = models.TextField()
    uuid = models.CharField(max_length=100, blank=True, null=True, default="Unrun Workflow")
    inputs = models.ManyToManyField("Input")
    outputs = models.CharField(max_length=300, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True) # TODO: Make a choice field

    def add_input(self, name, val):
        i = Input(name=name, value=val)
        i.save()

        self.inputs.add(i)

    # create the workflow run
    def create_workflow(self):
        # TODO
        # -move URL definition to settings file
        # -I guess this should use httplib for consistency
        url = "http://107.170.42.52:8080/taverna/rest/runs/"
        content_type = "application/vnd.taverna.t2flow+xml"


        b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS)).replace('\n', '')

        headers = {
            "Content-Type" : content_type,
            "Authorization": "Basic %s" % (b64),
        }

        req = urllib2.Request(url, self.t2flow, headers)


        response = urllib2.urlopen(req)
        
        try:
            uuid = response.info().getheader("Location")[len(url):]
            self.status = "Created"
            self.save()
            return uuid
        except:
            self.status = "Failed"
            self.save()
            return None

    # set up the inputs for the workflow run
    def send_inputs(self):
        for i in self.inputs.all():
            url = "/taverna/rest/runs/%s/input/input/%s" % (self.uuid, i.name)

            # hardcode this XML in for now
            data = "<t2sr:runInput xmlns:t2sr='http://ns.taverna.org.uk/2010/xml/server/rest/'>"
            data += "<t2sr:value>%s</t2sr>" % (i.value)
            data += "</t2sr:runInput>"

            b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS)).replace('\n', '')

            headers = {
                "Content-Type": "application/xml",
                "Authorization": "Basic %s" % (b64),
            }

            conn = httplib.HTTPConnection("107.170.42.52:8080")
            conn.request('PUT', url, data, headers)

            response = conn.getresponse()

            # TODO
            # Error Handling


    # starts the workflow running
    def start(self):
        url = "/taverna/rest/runs/%s/status" % (self.uuid)
        b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS)).replace('\n', '')

        headers = {
            "Content-Type": "text/plain",
            "Authorization": "Basic %s" % (b64),
        }

        conn = httplib.HTTPConnection("107.170.42.52:8080")
        conn.request('PUT', url, "Operating", headers)

        response = conn.getresponse()

        print "107.170.42.52:8080%s" %(url)
        self.status = "Operating"
        self.save()

    def __unicode__(self):
        return self.uuid

class Input(models.Model):
    name = models.CharField(max_length=50)
    value = models.TextField()

    def __unicode__(self):
        return self.name
