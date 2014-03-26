from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.core.context_processors import csrf
from django.template.loader import get_template
from django.template import RequestContext

from models import Job, Result, ABIFile, FASTAFile, TavernaWorkflow
from forms import JobForm

def add_job(request):
    if request.method == "POST":
        form = JobForm(request.POST, request.FILES)

        if form.is_valid():

            # create the new job
            job = create_job(form)

            # save the file
            path = handle_uploaded_file(request.FILES["file"])

            # create the initial sequence object
            sequence_object = create_sequence_object(path, job)

            if sequence_object is None:
                return HttpResponse("Bad Upload")
            else:
                return HttpResponse("nice")
    else:
        form = JobForm()

    t = get_template("add.html")
    c = RequestContext(request, {
        "form": form,
    })

    c.update(csrf(request))




    t2 = TavernaWorkflow.objects.get(pk=1)
    t2.create_workflow()

    return HttpResponse(t.render(c))



# Creates a job given the name, might need to beef this up a bit later
def create_job(form):
    j = Job(name=form.cleaned_data["name"])
    j.save()
    return j


# TODO:
# Send job to taverna
# create FASTA or ABI File
def handle_uploaded_file(f):

    # save the file
    path = "/Users/brentmitton/Desktop/CS/bioinf/project/abi_blaster/blaster/uploads/"+f.name

    with open(path, "w") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return path



def create_sequence_object(path, job):
    # this is not very intelligent. If the string ends with fasta extension
    # create a fasta, if it ends with ABI create an ABI

    sequence_object = None

    if path[-3:].lower() == "sta":
        print "Test"
        sequence_object = FASTAFile(path=path, job=job)
    elif path[-3:].lower() == "abi":
        print "test"
        sequence_object = ABIFile(path=path, job=job)

    return sequence_object
