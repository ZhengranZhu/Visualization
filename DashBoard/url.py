from django.urls import path
from . import views

urlpatterns = [
    path("v2/Dashboard/throughput", views.AllThroughputTime.as_view()),
    path("v2/Dashboard/productivity", views.AllProductivity.as_view()),
    path("v2/Dashboard/attendance_cnc_table", views.AttendanceCNC.as_view()),
    path("v2/Dashboard/attendance_assembly_table", views.AttendanceAss.as_view()),
    path("v2/Dashboard/throughput_compressor_table", views.ThroughputCompressor.as_view()),
    path('v2/Dashboard/throughput_past_alu', views.ThroughputTimePastAlu.as_view()),
    path('v2/Dashboard/throughput_past_sh', views.ThroughputTimePastSh.as_view()),
    path('v2/Dashboard/throughput_past_sc', views.ThroughputTimePastSc.as_view()),
    path("v2/Dashboard/Productivity_monthly", views.ProductivityMonthly.as_view()),
    ]


