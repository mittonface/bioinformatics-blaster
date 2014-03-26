from django.db import models
import urllib2
import base64

STATUS_CHOICES = (
    ("C", "Complete"),
    ("R", "Running"),
    ("F", "Failed"),
)

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

    def add_input(self, name, val):
        i = Input(name=name, value=val)
        i.save()

        self.inputs.add(i)

    def run_workflow(self):
        # TODO
        # move URL definition to settings file
        url = "http://107.170.42.52:8080/taverna/rest/runs"
        
        content_type = "application/vnd.taverna.t2flow+xml"
        b64 = base64.encodestring("%s:%s" % ("taverna", "taverna"))

        headers = {
            "Content-Type" : content_type,
            "Authorization": "Basic %s" % (b64),
        }

        req = urllib2.Request(url, self.t2flow, headers)


        response = urllib2.urlopen(req)
        print response

    def __unicode__(self):
        return self.uuid

class Input(models.Model):
    name = models.CharField(max_length=50)
    value = models.TextField()

    def __unicode__(self):
        return self.name
