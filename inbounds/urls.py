from django.urls import path
from . import views

app_name = 'inbounds'
urlpatterns = [
    path('', views.InboundListView.as_view(), name='inbound_list'),
]
