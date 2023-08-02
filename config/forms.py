from django import forms
from . import models

class ServerCreateForm(forms.ModelForm):
    parent_server = forms.ModelChoiceField(queryset=models.Server.objects.filter(parent_server__isnull=True))
    auth_key = forms.CharField(required=False)

    def clean_auth_key(self):
        if self.cleaned_data['parent_server'] and not self.cleaned_data['auth_key']:
            return forms.ValidationError('Child servers must have an auth key!')
        return self.cleaned_data

    class Meta:
        model = models.Server
        exclude = ('is_local_server', 'status')
