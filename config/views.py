from django.views.generic import ListView
from . import models


class ServerListView(ListView):
    model = models.Server
    template_name = 'pages/server_list.html'
    context_object_name = 'server_list'
