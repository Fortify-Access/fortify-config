from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from . import forms


class ServerListView(LoginRequiredMixin, ListView):
    model = models.Server
    template_name = 'config/server_list.html'
    context_object_name = 'servers'
    queryset = models.Server.objects.filter(parent_server__isnull=True)


class ServerCreateView(LoginRequiredMixin, CreateView):
    model = models.Server
    template_name = 'config/server_create.html'
    form_class = forms.ServerCreateForm
