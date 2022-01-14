import pandas as pd

from Visualization.settings import ldapserver, se_dn,se_pw,base_dn,attrs,filter
import ldap
from rest_framework.views import APIView
from Data_aquisition.serializaer import AttendanceAssFactSerializer, AttendanceCncFactSerializer, ManufacturingFactSerializer
from Data_aquisition.models import ManufacturingFact, ProductionLineAttendanceFact, DailyAttendanceCncFact, DailyAttendanceAssFact, TemperorayProductivityTable
from rest_framework.response import Response
from rest_framework import status
from pyecharts.charts import Gauge
from ThroughtputTime.charts import Pie_charts, Line_charts, Bar_charts, Line_bar_charts, Gauge_charts
from pyecharts import options as opts
from datetime import datetime
from django.db.models import Avg, Count, Sum
from calendar import monthrange


def allDays(y, m):
    return ['{:02d}-{:02d}'.format(m, d) for d in range(1, monthrange(y, m)[1] + 1)]

def allDays_v2(y, m):
    return ['{:04d}{:02d}{:02d}'.format(y, m, d) for d in range(1, monthrange(y, m)[1] + 1)]

# Create your views here.


class AttendanceCNC(APIView):
    def get(self, request, *args, **kwargs):

        date_option = request.GET.get("date")
        line_option = request.GET.get("line")

        query_set = DailyAttendanceCncFact.objects.filter(Date=date_option)


        serialized_query_set = AttendanceCncFactSerializer(instance=query_set, many=True)

        return Response(serialized_query_set.data)


class AttendanceAss(APIView):
    def get(self, request, *args, **kwargs):

        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        query_set = DailyAttendanceAssFact.objects.filter(Date=date_option)
        serialized_query_set = AttendanceAssFactSerializer(instance=query_set, many=True)


        return Response(serialized_query_set.data)


class AllThroughputTime(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_month = datetime.now().month
        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__MonthOfYear=this_month).values(
            'PackagingStartDateKey__MonthOfYear').order_by(
            'PackagingStartDateKey__MonthOfYear').annotate(average_throughputTime=Avg('AllThroughputTime'))

        throughput_time = []
        for item in query_set:
            throughput_time = round(item['average_throughputTime']/60, 2)

        b = Gauge_charts('Monthly Average Throughput Time', throughput_time, low=0.5, color_low="#10823E",
                         mid=0.8, color_mid="#FF8C00", high=1, color_high="#D83B01", min_1=0, max_1=150)

        return Response(b)


class AllProductivity(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_month = datetime.now().month

        prod = ManufacturingFact.objects.filter(PackagingStartDateKey__MonthOfYear=this_month).values('PackagingStartDateKey__MonthOfYear').annotate(
            total_cnc_hours=Sum('ProductFamilyKey__CncStandardTime'),
            total_ass_hours=Sum('ProductFamilyKey__StandardManufacturingTime')).order_by('PackagingStartDateKey__MonthOfYear')

        total_attendance_hours = ProductionLineAttendanceFact.objects.filter(Date__MonthOfYear=this_month).values('Date__MonthOfYear').annotate(total_hours=Sum('All')).order_by('Date__MonthOfYear')

        productivity = round((prod[0]['total_cnc_hours'] + prod[0]['total_ass_hours'])/(60*total_attendance_hours[0]['total_hours']), 2)

        b = Gauge_charts('Monthly Average Productivity', productivity, low=0.5, color_low="#D83B01"
                         , mid=0.7, color_mid="#FF8C00", high=1, color_high="#10823E", min_1=0, max_1=1)

        return Response(b)

class ThroughputCompressor(APIView):

    def get(self, request, *args, **kwargs):

        date_option = request.GET.get('date')
        line_option = request.GET.get('line')

        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey=date_option, ProductionLine=line_option).values()


        serialized_query_set = ManufacturingFactSerializer(instance=query_set, many=True)


        return Response(serialized_query_set.data)




class ProductivityMonthly(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_month = datetime.now().month
        this_year = datetime.now().year
        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__MonthOfYear=this_month).values(
            'PackagingStartDateKey').annotate(
            total_cnc_hours=Sum('ProductFamilyKey__CncStandardTime'),
            total_ass_hours=Sum('ProductFamilyKey__StandardManufacturingTime')).order_by('PackagingStartDateKey')
        attendance_this_month = ProductionLineAttendanceFact.objects.filter(Date__MonthOfYear=this_month).values('All', 'Date')
        temporeray_data = TemperorayProductivityTable.objects.values().all()


        a = allDays_v2(this_year, this_month)
        b = allDays(this_year, this_month)

        productivity_monthly = [0] * len(a)
# !!!!!!!!!!!!!!! code below should be uncomment when using all real production data
        for item in query_set:
            for attendance in attendance_this_month:
                if item['PackagingStartDateKey'] == attendance['Date']:

                    productivity_monthly[a.index(item['PackagingStartDateKey'])] = round((item['total_cnc_hours'] + item[
                        'total_ass_hours'])/(60*attendance['All']), 2)
# remove this line when officially release
        productivity_monthly[2] = 0.35
        b = Line_charts('Daily Productivity', b, productivity_monthly)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         for item in temporeray_data:
#             for attendance in attendance_this_month:
#                 if item['Date'] == attendance['Date']:
#
#                     productivity_monthly[a.index(item['Date'])] = round((item['ALUMSK'] + item['SC']+ item['SH'] + item['SCR'])/(attendance['All']*60), 2)
#
#         b = Line_charts('30 Days Productivity', a, productivity_monthly)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return Response(b)









class ThroughputTimePastAlu(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        manufacturing = ManufacturingFact.objects.filter(ProductionLine='ALU&MSK').values('SerialNumber','AllThroughputTime').order_by('-PackagingStartTime')[:25]

        throughput_time_alu = [round(item['AllThroughputTime']/60, 1) for item in manufacturing]
        serial_number = [item['SerialNumber'] for item in manufacturing]


        b = Bar_charts('Alu RealTime ThroughputTime', 'hours', serial_number, throughput_time_alu)
        return Response(b)
#
#
#
#
#
#
class ThroughputTimePastSh(APIView):

    def get(self, request, *args, **kwargs):

        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        manufacturing = ManufacturingFact.objects.filter(ProductionLine='SH').values('SerialNumber', 'AllThroughputTime').order_by('-PackagingStartTime')[:20]

        throughput_time_alu = [round(item['AllThroughputTime'] / 60, 1) for item in manufacturing]
        serial_number = [item['SerialNumber'] for item in manufacturing]


        b = Bar_charts('SH RealTime ThroughputTime', 'hours', serial_number, throughput_time_alu)
        return Response(b)



#
class ThroughputTimePastSc(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")

        manufacturing = ManufacturingFact.objects.filter(ProductionLine='SC').values('SerialNumber', 'AllThroughputTime').order_by('-PackagingStartTime')[:20]

        throughput_time_alu = [round(item['AllThroughputTime'] / 60, 1) for item in manufacturing]
        serial_number = [item['SerialNumber'] for item in manufacturing]

        b = Bar_charts('SC RealTime ThroughputTime', 'hours', serial_number, throughput_time_alu)
        return Response(b)

