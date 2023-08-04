from django.urls import path
from . import views

app_name = 'inbounds'
urlpatterns = [
    path('list/', views.InboundListView.as_view(), name='inbound_list'),
    path('create/', views.InboundCreateView.as_view(), name='inbound_create'),
    path('detail/<int:pk>/', views.InboundDetailView.as_view(), name='inbound_detail'),
    path('errors/<int:pk>/', views.InboundErrorListView.as_view(), name='inbound_errors'),
]
