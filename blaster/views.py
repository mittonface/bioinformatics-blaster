from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.core.context_processors import csrf
from django.template.loader import get_template
from django.template import RequestContext

from models import Job, Result, MultiFASTAFile, TavernaWorkflow, StoredWorkflows
from forms import JobForm

# TODO
# Clean up this function
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

                # now I want to create the workflow
                # TODO
                # add select workflow to the form. For now I'm just running this
                # only one that we have
                workflow = StoredWorkflows.objects.get(pk=1)
                t2 = TavernaWorkflow(t2flow=workflow.t2flow, job=job)
                t2.save()

                # now we should have a taverna workflow that tomcat is aware of
                # need to pass it some inputs now.

                with open(path, "r") as sequence_file:
                    print "here?"
                    t2.add_input("multiFasta",
                                 sequence_file.read().replace("\n", ''))

                    t2.add_input("email", form.cleaned_data["email"])


                return HttpResponse("nice")
    else:
        form = JobForm()

    t = get_template("add.html")
    c = RequestContext(request, {
        "form": form,
    })

    c.update(csrf(request))


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


# this method just exists because I had originally intended to accept
# fasta and ABI files. But I think ABIs are too proprietary for this
# assignment
def create_sequence_object(path, job):

    sequence_object = None

    if path[-3:].lower() == "sta":
        print "Test"
        sequence_object = MultiFASTAFile(path=path, job=job)

    return sequence_object
