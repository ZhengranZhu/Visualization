from django.urls import path
from . import views

urlpatterns = [
    path("v2/Throughput/alu", views.ThroughputAlu.as_view()),
    path("v2/Throughput/msk", views.ThroughputMsk.as_view()),
    path("v2/Throughput/sc", views.ThroughputSc.as_view()),
    path("v2/Throughput/scr", views.ThroughputScr.as_view()),
    path("v2/Throughput/sh", views.ThroughputSh.as_view()),

]