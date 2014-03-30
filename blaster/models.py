from django.db import models
from django.conf import settings
import urllib2
import httplib
import base64

# I'd like to turn this into a complete taverna wrapper at some point.
# for now it's just going to serve the purpose of getting my assignment
# done
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




# FASTA files may come from ABI files or be uploaded directly. In the first 
# case we will want to create a link to the parent ABI File. FASTA files will
# be the primary type of object we're operating on. So results will link back
# to fastas
class MultiFASTAFile(models.Model):
    path = models.CharField(max_length=300)
    job = models.ForeignKey(Job)


class Result(models.Model):
    fasta = models.ForeignKey(MultiFASTAFile)
    text = models.CharField(max_length=50) # I want to see what I'm working
                                           # with before i expand on this


# This probably doesnt need to be a django model, but I think it's helpful to
# me if I can manage them here
class TavernaWorkflow(models.Model):
    t2flow = models.TextField()
    uuid = models.CharField(max_length=100, blank=True, null=True, default="Unrun Workflow")
    inputs = models.ManyToManyField("Input", blank=True, null=True)
    outputs = models.CharField(max_length=300, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True) # TODO: Make a choice field
    job = models.ForeignKey(Job)


    # I want these to related to an object on my taverna server. that means
    # on creation, I want to create a t2flow flow on the taverna server.
    def save(self, *args, **kwargs):

        # workflow creation
        if not self.pk:
            self.uuid = self.create_workflow()

        super(TavernaWorkflow, self).save(*args, **kwargs)


    # on deletion I want to remove this workflow from the taverna server
    def delete(self, *args, **kwargs):
        # deletion

        url = "/taverna/rest/runs/%s" % (self.uuid)
        b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS)).replace('\n', '')

        headers = {
            "Authorization": "Basic %s" % (b64),
        }

        conn = httplib.HTTPConnection("107.170.42.52:8080")
        conn.request('DELETE', url, "", headers)

        response = conn.getresponse()

        super(TavernaWorkflow, self).delete(*args, **kwargs)


    # TODO:
    # it might be better to do this within a manager or on the input class 
    # I'll have to think about that a bit more. 
    def add_input(self, name, val):
        i = Input(name=name, value=val)
        i.save()

        self.inputs.add(i)
        self.send_inputs()  # hopefully inputs will overwrite


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
            return uuid
        except:
            self.status = "Failed"
            return None


    # set up the inputs for the workflow run
    def send_inputs(self):
        for i in self.inputs.all():
            url = "/taverna/rest/runs/%s/input/input/%s" % (self.uuid, i.name)

            # hardcode this XML in for now
            data = "<t2sr:runInput xmlns:t2sr='http://ns.taverna.org.uk/2010/xml/server/rest/'>"
            data += "<t2sr:value>%s</t2sr:value>" % (i.value)
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
        b64 = base64.encodestring("%s:%s" % (TAVERNA_USER, TAVERNA_PASS))

        headers = {
            "Content-Type": "text/plain",
            "Authorization": "Basic %s" % (b64),
        }

        conn = httplib.HTTPConnection("107.170.42.52:8080")
        conn.request('PUT', url, "Operating", headers)

        response = conn.getresponse()

        self.status = "Operating"
        self.save()

    def __unicode__(self):
        return self.uuid

class Input(models.Model):
    name = models.CharField(max_length=50)
    value = models.TextField()

    def __unicode__(self):
        return self.name

# TODO:
# Make this more sophisticated. It could, for example, store information about
# expected inputs and outputs.
class StoredWorkflows(models.Model):
    t2flow = models.TextField()
