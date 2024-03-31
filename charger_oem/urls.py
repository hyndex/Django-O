from django.urls import path
from . import views

urlpatterns = [
    path('log_ip/', views.log_ip, name='log_ip'),
]
