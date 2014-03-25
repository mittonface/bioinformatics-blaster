from django import forms


class JobForm(forms.Form):
    name = forms.CharField(max_length=300, required=False)
    file = forms.FileField('uploads')



