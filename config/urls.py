from django.urls import path
from . import views

app_name = 'config'
urlpatterns = [
    path('', views.ServerListView.as_view(), name='server_list')
]
