from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from config import models as config_models
from . import models
from . import forms


class InboundListView(LoginRequiredMixin, ListView):
    model = models.Inbound
    template_name = 'inbounds/inbound_list.html'
    context_object_name = 'inbounds'


class InboundCreateView(LoginRequiredMixin, CreateView):
    model = models.Inbound
    template_name = 'inbounds/inbound_create.html'
    form_class = forms.InboundForm
    success_url = reverse_lazy('inbounds:inbound_list')

    def get_context_data(self, **kwargs):
        context = super(InboundCreateView, self).get_context_data(**kwargs)
        context['tls_form'] = forms.TlsForm(prefix='tls')
        context['user_form'] = forms.InboundUserForm(prefix='inbound_user')
        context['traffic_form'] = forms.TrafficForm(prefix='traffic')
        return context

    def form_valid(self, form):
        response = super(InboundCreateView, self).form_valid(form)
        tls_form = forms.TlsForm(prefix='tls', data=self.request.POST)
        user_form = forms.InboundUserForm(prefix='inbound_user', data=self.request.POST)
        traffic_form = forms.TrafficForm(prefix='traffic', data=self.request.POST)

        if tls_form.is_valid() and user_form.is_valid() and traffic_form.is_valid():
            tls_instance, user_instance, traffic_instance = tls_form.save(commit=False), user_form.save(commit=False), traffic_form.save(commit=False)
            tls_instance.inbound, user_instance.inbound, traffic_instance.inbound = [self.object] * 3
            tls_instance.save()
            user_instance.save()
            traffic_instance.save()
            self.object.push()
            return response


class InboundDetailView(LoginRequiredMixin, DetailView):
    model = models.Inbound
    template_name = 'inbounds/inbound_detail.html'
    context_object_name = 'inbound'


class InboundErrorListView(LoginRequiredMixin, ListView):
    model = config_models.Log
    template_name = 'inbounds/inbound_errors.html'
    context_object_name = 'errors'

    def get_queryset(self):
        return config_models.Log.objects.filter(inbound=self.kwargs['pk'])
