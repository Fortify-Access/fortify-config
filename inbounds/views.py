from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from . import forms


class InboundListView(LoginRequiredMixin, ListView):
    model = models.Inbound
    template_name = 'inbounds/inbound_list.html'
    context_object_name = 'inbounds'


class InboundCreateView(LoginRequiredMixin, CreateView):
    model = models.Inbound
    template_name = 'inbounds/inbound_create.html'
    form_class = forms.InboundCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tls_form'] = forms.TlsCreateForm(prefix='tls')
        context['user_form'] = forms.InboundUserCreateForm(prefix='inbound_user')
        context['traffic_form'] = forms.TrafficCreateForm(prefix='traffic')
        return context


class InboundDetailView(LoginRequiredMixin, DetailView):
    model = models.Inbound
    template_name = 'inbounds/inbound_detail.html'
    context_object_name = 'inbound'
