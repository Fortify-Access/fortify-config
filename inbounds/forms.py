from django import forms
from . import models
from config import models as config_models


class InboundCreateForm(forms.ModelForm):
    server = forms.ModelChoiceField(queryset=config_models.Server.objects.filter(parent_server__isnull=True))

    class Meta:
        model = models.Inbound
        fields = '__all__'


class TlsCreateForm(forms.ModelForm):
    class Meta:
        model = models.Tls
        fields = '__all__'


class InboundUserCreateForm(forms.ModelForm):
    class Meta:
        model = models.InboundUser
        fields = '__all__'
        

class TrafficCreateForm(forms.ModelForm):
    class Meta:
        model = models.Traffic
        fields = ('allowed_traffic',)
