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
    path("v1/md_throughput_average", views.MdThroughputAverage.as_view()),
    path("v1/md_throughput_all", views.MdThroughputAll.as_view()),
    path("v1/md_throughput_alu", views.MdThroughtputAlu.as_view()),
    path("v1/md_throughput_scr", views.MdThroughtputScr.as_view()),
    path("v1/md_throughput_sc", views.MdThroughtputSc.as_view()),
    path("v1/md_throughput_sh", views.MdThroughtputSH.as_view()),
    path("v1/md_productivity_average", views.MdProductivityAverage.as_view()),
    path("v1/md_productivity_all", views.MdProductivityAll.as_view()),
    path("v1/dir_attendance_assy", views.AssAttendance.as_view()),
    path("v1/dir_attendance_cnc", views.CncAttendance.as_view()),
    path("v1/md_productivity_cnc_assy", views.MdProductivityCncAssy.as_view()),
    ]


