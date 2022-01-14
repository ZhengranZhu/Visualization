import pandas as pd

from Visualization.settings import ldapserver, se_dn,se_pw,base_dn,attrs,filter
import ldap
from rest_framework.views import APIView

from Data_aquisition.models import ManufacturingFact, ProductionLineAttendanceFact
from rest_framework.response import Response
from rest_framework import status
from pyecharts.charts import Gauge
from ThroughtputTime.charts import Pie_charts, Line_charts, Bar_charts, Line_bar_charts, Gauge_charts
from pyecharts import options as opts
import datetime
from django.db.models import Avg, Count


# Create your views here.
def get_throughput_by_day(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'
    throughput_time = []
    date_list = []
    week_num = pd.to_datetime(date_option1).isocalendar()[1]
    query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__WeekOfYear=week_num, ProductFamilyKey__ProductDescriptionEn='BIFA').values('PackagingStartDateKey').\
        order_by('PackagingStartDateKey').annotate(
        average_throughputTime=Avg(line))

    for item in query_set:
        date_list.append(item['PackagingStartDateKey'])
        throughput_time.append((round(item['average_throughputTime'], 2)))

    b = Bar_charts("all_week_throughput", 'Minutes', date_list, throughput_time)
    return b


def get_throughput_by_week(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'
    throughput_time = [0] * 52
    date_list = list(range(1, 53))

    query_set = ManufacturingFact.objects.filter(ProductFamilyKey__ProductDescriptionEn='BIFA').values('PackagingStartDateKey__WeekOfYear').order_by(
        'PackagingStartDateKey__WeekOfYear') \
        .annotate(average_throughputTime=Avg(line))

    for item in query_set:
        if item['PackagingStartDateKey__WeekOfYear'] in date_list:
            # date_list.append(item['TestingStartDateKey'])
            throughput_time[item['PackagingStartDateKey__WeekOfYear'] - 1] = round(item['average_throughputTime'], 2)

    b = Bar_charts("Weekly_throughputTime", "Minutes", date_list, throughput_time)
    return b


def get_throughput_by_month(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'

    throughput_time = [0] * 12
    date_list = list(range(1, 13))

    query_set = ManufacturingFact.objects.filter(ProductFamilyKey__ProductDescriptionEn='BIFA').values('PackagingStartDateKey__MonthOfYear').order_by(
        'PackagingStartDateKey__MonthOfYear').annotate(average_throughputTime=Avg(line))

    for item in list(query_set):
        if item['PackagingStartDateKey__MonthOfYear'] in date_list:
            # date_list.append(item['TestingStartDateKey'])
            throughput_time[item['PackagingStartDateKey__MonthOfYear'] - 1] = round(item['average_throughputTime'], 2)

    b = Bar_charts('Monthly_throughputTime', 'Minutes', date_list, throughput_time)

    return b


def get_throughput_by_year(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'
    year = int(date_option1[:4])

    throughput_time = [0] * 12
    date_list = list(range(year - 9, year + 1))

    query_set = ManufacturingFact.objects.filter(ProductFamilyKey__ProductDescriptionEn='BIFA').values('PackagingStartDateKey__CalendarYear').order_by(
        'PackagingStartDateKey__CalendarYear').annotate(average_throughputTime=Avg(line))

    for item in list(query_set):

        if item['PackagingStartDateKey__CalendarYear'] in date_list:
            # date_list.append(item['TestingStartDateKey'])

            throughput_time[date_list.index(item['PackagingStartDateKey__CalendarYear'])] = round(item[
                'average_throughputTime'], 2)

    b = Bar_charts('yearly_throughputTime', 'Minutes', date_list, throughput_time)
    return b


class ThroughputAlu(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        print(line_option, date_option, limit_option)

        if limit_option == 'day':

            b = get_throughput_by_day(date_option1=date_option, line_option1=line_option)
            return Response(b)

        elif limit_option == 'week':

            b = get_throughput_by_week(date_option1=date_option, line_option1=line_option)
            return Response(b)

        elif limit_option == 'month':

            b = get_throughput_by_month(date_option1=date_option, line_option1=line_option)
            return Response(b)

        elif limit_option == 'year':
            b = get_throughput_by_year(date_option1=date_option, line_option1=line_option)
            return Response(b)


class ThroughputMsk(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")

        return "e"


class ThroughputSc(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")

        return "e"


class ThroughputScr(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")

        return "e"


class ThroughputSh(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")


        return "e"

def get_productivity_by_day(date_option1, line_option1):
    throughput_time = []
    date_list = []
    week_num = pd.to_datetime(date_option1).isocalendar()[1]
    total_compressors = ManufacturingFact.objects.filter(PackagingStartDateKey__WeekOfYear=week_num).values('PackagingStartDateKey'
                                                                                                            ).annotate(dcount=Count('PackagingStartDateKey')).order_by(
        'PackagingStartDateKey'
    )

    total_attendance_hours = ProductionLineAttendanceFact.objects.filter()



class ProductivityAlu(APIView):
    def get(self, request, *args, **kwargs):

        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        limit_option = request.GET.get('limit')

        if limit_option == 'day':

            query_set = ManufacturingFact.objects.filter(ProductFamilyKey__ProductDescriptionEn='BIFA').values()
        # elif limit_option == 'week':
        #
        # elif limit_option == 'month':
        #
        # elif limit_option == 'year':





        return 'E'
