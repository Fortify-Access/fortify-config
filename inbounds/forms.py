from django import forms
from django.utils.crypto import get_random_string
from . import models
from . import functions
from config import models as config_models


class InboundForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InboundForm, self).__init__(*args, **kwargs)
        self.fields['server'].queryset = config_models.Server.objects.filter(parent_server__isnull=True)
        self.fields['tag'].initial = get_random_string(8)
        self.fields['tag'].widget.attrs['readonly'] = True

    class Meta:
        model = models.Inbound
        fields = '__all__'


class TlsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TlsForm, self).__init__(*args, **kwargs)
        self.fields['private_key'].initial, self.fields['public_key'].initial = functions.get_reality_keypair()
        self.fields['short_id'].initial = functions.get_short_id()

    class Meta:
        model = models.Tls
        exclude = ('inbound', )


class InboundUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InboundUserForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = get_random_string(10)
        self.fields['uuid'].initial = functions.get_uuid()

    class Meta:
        model = models.InboundUser
        exclude = ('inbound', )
        

class TrafficForm(forms.ModelForm):
    def clean_allowed_traffic(self):
        self.cleaned_data['allowed_traffic'] = self.cleaned_data['allowed_traffic'] * 1000000000
        return self.cleaned_data['allowed_traffic']

    class Meta:
        model = models.Traffic
        fields = ('allowed_traffic',)
