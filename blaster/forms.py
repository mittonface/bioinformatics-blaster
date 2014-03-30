from django import forms


class JobForm(forms.Form):
    name = forms.CharField(max_length=300, required=True)
    file = forms.FileField('uploads')
    email = forms.EmailField(required=True)



