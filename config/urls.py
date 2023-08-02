from django.urls import path
from . import views

app_name = 'config'
urlpatterns = [
    path('server/list/', views.ServerListView.as_view(), name='server_list'),
    path('server/create/', views.ServerCreateView.as_view(), name='server_create')
]
