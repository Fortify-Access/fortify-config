from django.urls import path
from . import views

app_name = 'inbounds'
urlpatterns = [
        path('', views.inbound_list, name="inbound_list"),
]
