from django.urls import path
from . import views

app_name = 'inbounds'
urlpatterns = [
        path('', views.InboundsView.as_view(), name="inbound_list"),
        path('add/', views.AddInboundView.as_view(), name="add_inbound"),
]
