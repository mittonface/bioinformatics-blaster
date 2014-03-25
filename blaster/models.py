from django.db import models

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


