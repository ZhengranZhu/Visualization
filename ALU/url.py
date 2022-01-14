from django.urls import path
from . import views

urlpatterns = [
    path("v2/Throughput/alu", views.ThroughputAlu.as_view()),
    path("v2/Productivity/alu", views.ProductivityAlu.as_view()),
    ]