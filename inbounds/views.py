from django.views.generic import ListView
from . import models


class InboundListView(ListView):
    model = models.Inbound
    template_name = 'pages/inbound_list.html'
    context_object_name = 'inbound_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print([inbound for inbound in models.Inbound.objects.all()])
        return context
