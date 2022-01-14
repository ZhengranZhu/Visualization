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
from django.db.models import Avg, Count, Aggregate, Sum


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
    print(query_set)
    for item in query_set:
        date_list.append(item['PackagingStartDateKey'])
        throughput_time.append((round(item['average_throughputTime'], 2)))
    print(throughput_time)
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
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'
    week_num = pd.to_datetime(date_option1).isocalendar()[1]
    total_compressors = ManufacturingFact.objects.filter(PackagingStartDateKey__WeekOfYear=week_num).values(
        'PackagingStartDateKey', 'ProductFamilyKey__StandardManufacturingTime',
        'ProductFamilyKey__CncStandardTime'
    ).annotate(dcount=Count('PackagingStartDateKey')).order_by()
    total_attendance_hours = ProductionLineAttendanceFact.objects.filter(Date__WeekOfYear=week_num).values(
        'Cnc', 'Date')

    weekdates = get_week_dates_from_date(date_option1)

    productivities = [0] * 7
    #
    for compressor in total_compressors:
        for attendance in total_attendance_hours:

            if compressor['PackagingStartDateKey'] == attendance['Date']:
                productivity = round(
                    compressor['dcount'] * compressor['ProductFamilyKey__StandardManufacturingTime'] / attendance[
                        'Cnc'], 2)
                productivities[weekdates.index(attendance['Date'])] = productivity


    b = Bar_charts('Dayily Alu Productivity', '%', weekdates, productivities)
    return b

def get_productivity_by_week(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'

    year_num = pd.to_datetime(date_option1).isocalendar()[0]
    week_list = list(range(1, 53))
    total_compressors = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=year_num).values(
        'ProductFamilyKey__StandardManufacturingTime',
        'ProductFamilyKey__CncStandardTime', 'PackagingStartDateKey__WeekOfYear'
    ).annotate(dcount=Count('PackagingStartDateKey__WeekOfYear')).order_by('PackagingStartDateKey__WeekOfYear')
    total_attendance_hours = ProductionLineAttendanceFact.objects.filter(Date__CalendarYear=year_num).values(
        'Date__WeekOfYear').values('Date__WeekOfYear').annotate(total_hours=Sum('All'))

    productivities = [0] * 52
    #
    for compressor in total_compressors:
        for attendance in total_attendance_hours:

            if compressor['PackagingStartDateKey__WeekOfYear'] == attendance['Date__WeekOfYear']:

                productivity = round(
                    compressor['dcount'] * compressor['ProductFamilyKey__StandardManufacturingTime'] / attendance[
                        'total_hours'], 2)
                productivities[week_list.index(attendance['Date__WeekOfYear'])] = productivity

    b = Bar_charts('Weekly Alu Productivity', '%', week_list, productivities)
    return b

def get_productivity_by_month(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'

    productivities = [0] * 12
    month_list = list(range(1, 13))
    year_num = pd.to_datetime(date_option1).isocalendar()[0]
    total_compressors = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=year_num).values(
        'ProductFamilyKey__StandardManufacturingTime',
        'ProductFamilyKey__CncStandardTime', 'PackagingStartDateKey__MonthOfYear'
    ).annotate(dcount=Count('PackagingStartDateKey__MonthOfYear')).order_by('PackagingStartDateKey__MonthOfYear')
    total_attendance_hours = ProductionLineAttendanceFact.objects.filter(Date__CalendarYear=year_num).values(
        'Date__MonthOfYear').values('Date__MonthOfYear').annotate(total_hours=Sum('All'))
    #
    print(total_attendance_hours)
    for compressor in total_compressors:
        for attendance in total_attendance_hours:

            if compressor['PackagingStartDateKey__MonthOfYear'] == attendance['Date__MonthOfYear']:
                productivity = round(
                    compressor['dcount'] * compressor['ProductFamilyKey__StandardManufacturingTime'] / attendance[
                        'total_hours'], 2)
                productivities[month_list.index(attendance['Date__MonthOfYear'])] = productivity
    print(productivities)

    b = Bar_charts('Monthly Alu Productivity', '%', month_list, productivities)
    return b

def get_productivity_by_year(date_option1, line_option1):
    if line_option1 == 'all':
        line = 'AllThroughputTime'
    elif line_option1 == 'cnc':
        line = 'CncThroughputTime'
    elif line_option1 == 'ass':
        line = 'AssThroughputTime'
    else:
        line = 'AssThroughputTime'

    year_num = date_option1[:4]

    productivities= [0] * 10
    year_list = list(range(int(year_num) - 9, int(year_num) + 1))
    #year_list = [str(item) for item in year_list]
    print(year_list)

    total_compressors = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=year_num).values(
        'ProductFamilyKey__StandardManufacturingTime',
        'ProductFamilyKey__CncStandardTime', 'PackagingStartDateKey__CalendarYear'
    ).annotate(dcount=Count('PackagingStartDateKey__CalendarYear')).order_by('PackagingStartDateKey__CalendarYear')
    total_attendance_hours = ProductionLineAttendanceFact.objects.filter(Date__CalendarYear=year_num).values('Date__CalendarYear').annotate(total_hours=Sum('All'))



    for compressor in total_compressors:
        for attendance in total_attendance_hours:

            if compressor['PackagingStartDateKey__CalendarYear'] == attendance['Date__CalendarYear']:

                productivity = round(
                    compressor['dcount'] * compressor['ProductFamilyKey__StandardManufacturingTime'] / attendance[
                        'total_hours'], 2)
                print(year_list.index(attendance['Date__CalendarYear']))
                productivities[year_list.index(attendance['Date__CalendarYear'])] = productivity


    b = Bar_charts('Monthly Alu Productivity', '%', year_list, productivities)
    return b


class ProductivityAlu(APIView):
    def get(self, request, *args, **kwargs):

        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        limit_option = request.GET.get('limit')
        week_num = pd.to_datetime(date_option).isocalendar()[1]
        if limit_option == 'day':
            b = get_productivity_by_day(date_option1=date_option, line_option1=line_option)
            return Response(b)

        elif limit_option == 'week':
            b = get_productivity_by_week(date_option1=date_option, line_option1=line_option)
            return Response(b)

        elif limit_option == 'month':
            b = get_productivity_by_month(date_option1=date_option, line_option1=line_option)
            return Response(b)

        elif limit_option == 'year':
            b = get_productivity_by_year(date_option1=date_option, line_option1=line_option)
            return Response(b)


def get_week_dates_from_date(date):
    # Helper function to return all dates in a week in string format with given date
    from datetime import datetime, timedelta
    d = datetime.strptime(date, '%Y%m%d').isoweekday()
    week_dates = [datetime.strptime(date, '%Y%m%d') - timedelta(days=i) for i in range(d - 1, -1, -1)]
    week_dates1 = [datetime.strptime(date, '%Y%m%d') + timedelta(days=i + 1) for i in range(7 - d)]
    weekdates = [datetime.strftime(item, '%Y%m%d') for item in week_dates + week_dates1]

    return weekdates
