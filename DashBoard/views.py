import pandas as pd
import json
from Visualization.settings import ldapserver, se_dn,se_pw,base_dn,attrs,filter
import ldap
from rest_framework.views import APIView
from Data_aquisition.serializaer import AttendanceAssFactSerializer, AttendanceCncFactSerializer, ManufacturingFactSerializer
from Data_aquisition.models import ManufacturingFact, ProductionLineAttendanceFact, DailyAttendanceAssFact, DailyAttendanceCncFact, TemperorayProductivityTable
from rest_framework.response import Response
from django.db.models import F
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

        if len(list(total_attendance_hours)) == 0:
            productivity = 0
        else:
            productivity = round((prod[0]['total_cnc_hours'] + prod[0]['total_ass_hours']) / (
                        60 * total_attendance_hours[0]['total_hours']), 2)


        b = Gauge_charts('Monthly Average Productivity', productivity, low=0.5, color_low="#D83B01"
                         , mid=0.7, color_mid="#FF8C00", high=1, color_high="#10823E", min_1=0, max_1=1)

        return Response(b)

class ThroughputCompressor(APIView):

    def get(self, request, *args, **kwargs):

        date_option = request.GET.get('date')
        line_option = request.GET.get('line')
        period_option = request.GET.get('period')

        this_week = datetime.strptime(date_option, "%Y%m%d").isocalendar()[1]
        this_month = datetime.strptime(date_option, "%Y%m%d").month
        this_quarter = (this_month - 1) // 3 + 1
        this_year = date_option[0:4]

        if period_option == 'day':
            query_set = ManufacturingFact.objects.filter(PackagingStartDateKey=date_option,
                                                         ProductionLine=line_option).values()
            serialized_query_set = ManufacturingFactSerializer(instance=query_set, many=True)
            return Response(serialized_query_set.data)
        elif period_option == 'month':
            query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__MonthOfYear=this_month,
                                                         ProductionLine=line_option).values()
            serialized_query_set = ManufacturingFactSerializer(instance=query_set, many=True)

            return Response(serialized_query_set.data)
        elif period_option == 'week':
            query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__WeekOfYear=this_week,
                                                         ProductionLine=line_option).values()
            serialized_query_set = ManufacturingFactSerializer(instance=query_set, many=True)

            return Response(serialized_query_set.data)
        elif period_option == 'year':
            query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year,
                                                         ProductionLine=line_option).values()
            serialized_query_set = ManufacturingFactSerializer(instance=query_set, many=True)
            return Response(serialized_query_set.data)

        elif period_option == 'quarter':
            query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__FiscalQuarter=this_quarter,
                                                         ProductionLine=line_option).values()
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
#         productivity_monthly[2] = 0.35
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

# class MdThroughputAverage(APIView):
#
#     def get(self, request, *args, **kwargs):
#         limit_option = request.GET.get("limit")
#         date_option = request.GET.get("date")
#         line_option = request.GET.get("line")
#
#         this_year = datetime.now().year
#         query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear==this_year).values(
#             'PackagingStartDateKey__MonthOfYear').order_by(
#             'PackagingStartDateKey__MonthOfYear').annotate(average_throughputTime=Avg('AllThroughputTime'))
class MdThroughputAverage(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")

        this_year = datetime.now().year
        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).values(
            'PackagingStartDateKey__CalendarYear').order_by(
            'PackagingStartDateKey__CalendarYear').annotate(average_throughputTime=Avg('AllThroughputTime'))
        throughput_time = []
        for item in query_set:
            throughput_time = round(item['average_throughputTime'] / 60, 2)

        throughput_time_dict = {"values": throughput_time}
        return Response(json.dumps(throughput_time_dict))


class MdThroughputAll(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = datetime.now().year

        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).values(
            'PackagingStartDateKey__MonthOfYear').order_by(
            'PackagingStartDateKey__MonthOfYear').annotate(average_throughputTime=Avg('AllThroughputTime'))


        throughput_time = []
        for item in query_set:
            throughput_time.append(round(item['average_throughputTime'] / 60, 2))


        throughput_time_dict = {"values": throughput_time}
        return Response(json.dumps(throughput_time_dict))


class MdThroughtputAlu(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]

        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).filter(PackagingStartDateKey__MonthOfYear=this_month).filter(ProductFamilyKey__ProductDescriptionEn='ALU&MSK').values('PackagingStartDateKey').order_by('PackagingStartDateKey').annotate(average_throughputTime=Avg('AllThroughputTime'))

        throughput_time = [0]*31
        for item in query_set:
            throughput_time[int(item['PackagingStartDateKey'][-2:])-1] = round(item['average_throughputTime']/60, 1)

        throughput_time_dict = {"values": throughput_time}
        return Response(json.dumps(throughput_time_dict))


class MdThroughtputScr(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]

        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).filter(
            PackagingStartDateKey__MonthOfYear=this_month).filter(
            ProductFamilyKey__ProductDescriptionEn='SCR').values('PackagingStartDateKey').order_by(
            'PackagingStartDateKey').annotate(average_throughputTime=Avg('AllThroughputTime'))
        throughput_time = [0]*31
        for item in query_set:
            throughput_time[int(item['PackagingStartDateKey'][-2:])-1] = round(item['average_throughputTime']/60, 1)

        throughput_time_dict = {"values": throughput_time}
        return Response(json.dumps(throughput_time_dict))


class MdThroughtputSc(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]

        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).filter(
            PackagingStartDateKey__MonthOfYear=this_month).filter(
            ProductFamilyKey__ProductDescriptionEn='SC').values('PackagingStartDateKey').order_by(
            'PackagingStartDateKey').annotate(average_throughputTime=Avg('AllThroughputTime'))

        throughput_time = [0]*31

        for item in query_set:
            throughput_time[int(item['PackagingStartDateKey'][-2:])-1] = round(item['average_throughputTime']/60, 1)
        throughput_time_dict = {"values": throughput_time}
        return Response(json.dumps(throughput_time_dict))


class MdThroughtputSH(APIView):

    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]

        query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).filter(
            PackagingStartDateKey__MonthOfYear=this_month).filter(
            ProductFamilyKey__ProductDescriptionEn='SH').values('PackagingStartDateKey').order_by(
            'PackagingStartDateKey').annotate(average_throughputTime=Avg('AllThroughputTime'))
        throughput_time = [0]*31
        for item in query_set:
            throughput_time[int(item['PackagingStartDateKey'][-2:])-1] = round(item['average_throughputTime']/60, 1)
        throughput_time_dict = {"values": throughput_time}
        return Response(json.dumps(throughput_time_dict))


class MdProductivityAverage(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]

        prod = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).values(
            'PackagingStartDateKey__CalendarYear').annotate(
            total_cnc_hours=Sum('ProductFamilyKey__CncStandardTime'),
            total_ass_hours=Sum('ProductFamilyKey__StandardManufacturingTime')).order_by(
            'PackagingStartDateKey__CalendarYear')
        total_attendance_hours = ProductionLineAttendanceFact.objects.filter(Date__CalendarYear=this_year).values(
            'Date__CalendarYear').annotate(total_hours=Sum('All')).order_by('Date__CalendarYear')

        productivity = round(100*
            (prod[0]['total_cnc_hours'] + prod[0]['total_ass_hours']) / (60 * total_attendance_hours[0]['total_hours']),
            1)

        productivity_dict = {"values": productivity}
        return Response(json.dumps(productivity_dict))


class MdProductivityAll(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]

        if limit_option == 'month':
            prod = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).values(
                'PackagingStartDateKey__MonthOfYear').annotate(
                total_cnc_hours=Sum('ProductFamilyKey__CncStandardTime'),
                total_ass_hours=Sum('ProductFamilyKey__StandardManufacturingTime')).order_by(
                'PackagingStartDateKey__MonthOfYear')

            total_attendance_hours = ProductionLineAttendanceFact.objects.filter(
                Date__CalendarYear=this_year).values(
                'Date__MonthOfYear').annotate(total_hours=Sum('All')).order_by('Date__MonthOfYear')

            productivity = [0]*12
            for item in total_attendance_hours:
                for pro in prod:
                    if item['Date__MonthOfYear'] == pro['PackagingStartDateKey__MonthOfYear']:
                        productivity[int(item['Date__MonthOfYear'])-1] = round(100*(pro['total_cnc_hours'] + pro['total_ass_hours'])/(60*item['total_hours']), 1)
            print(productivity)

            # for i in range(0, len(list(prod))):
            #     productivity.append(round(
            #         (prod[i]['total_cnc_hours'] + prod[i]['total_ass_hours']) / (
            #                 60 * total_attendance_hours[i]['total_hours']),
            #         2))

            productivity_dict = {"values": productivity}
            return Response(json.dumps(productivity_dict))

class MdProductivityCncAssy(APIView):
    def get(self, request, *args, **kwargs):
        limit_option = request.GET.get("limit")
        date_option = request.GET.get("date")
        line_option = request.GET.get("line")
        this_year = date_option[0:4]
        this_month = date_option[4:6]
        print(this_year)

        if limit_option == 'day':
            prod = ManufacturingFact.objects.filter(PackagingStartDateKey__CalendarYear=this_year).filter(PackagingStartDateKey__MonthOfYear=this_month).values('PackagingStartDateKey').annotate(total_cnc_hours=Sum('ProductFamilyKey__CncStandardTime'),total_ass_hours=Sum('ProductFamilyKey__StandardManufacturingTime')).order_by('PackagingStartDateKey')

            total_attendance_hours = ProductionLineAttendanceFact.objects.filter(
                Date__CalendarYear=this_year).filter(Date__MonthOfYear=this_month).values(
                'Date').annotate(total_hours=Sum('All')).order_by('Date')

            productivity = [0]*31
            for item in total_attendance_hours:
                for pro in prod:
                    if item['Date'] == pro['PackagingStartDateKey']:
                        productivity[int(item['Date'][-2:])-1] = round(100*(pro['total_cnc_hours'] + pro['total_ass_hours'])/(60*item['total_hours']), 1)

            # for i in range(0, len(list(prod))):
            #     productivity.append(round(
            #         (prod[i]['total_cnc_hours'] + prod[i]['total_ass_hours']) / (
            #                 60 * total_attendance_hours[i]['total_hours']),
            #         2))
            productivity_dict = {"values": productivity}
            return Response(json.dumps(productivity_dict))

# class AssAttendance(APIView):
#     def put(self, request, *args, **kwargs):
#         print(request.data)
#         number = str(request.data['number'])
#         value = float(request.data['value'])
#         date = str(request.data['date'])
#         print(request.data['number'], request.data['value'], request.data['date'])
#         att = DailyAttendanceAssFact.objects.filter(Pers_No=number, Date=date).update(Attendance_Time=value)
#
#         return Response(json.dumps({"values": "successful"}))
#
#
# class CncAttendance(APIView):
#     def put(self, request, *args, **kwargs):
#         number = str(request.data['number'])
#         value = float(request.data['value'])
#         date = str(request.data['date'])
#         # print(request.POST['number'], request.POST['value'], request.POST['date'])
#         att = DailyAttendanceCncFact.objects.filter(Pers_No=number, Date=date).update(Attendance_Time=value)
#
#         return Response(json.dumps({"values": "successful"}))

class AssAttendance(APIView):
    def put(self, request, *args, **kwargs):
        print(request.data)
        number = str(request.data['number'])
        value = float(request.data['value'])
        date = str(request.data['date'])
        print(number, value, date)
        att = DailyAttendanceAssFact.objects.filter(Pers_No=number).filter(Date=date).values()
        att_value_orig = att[0]['Attendance_Time']
        change_value = value - att_value_orig
        print(change_value, att[0]['Description'])

        if att[0]['CC'] in ['40602100.0', '40602110.0', '40602120.0', '40602130.0', '40602140.0']:
            DailyAttendanceAssFact.objects.filter(Pers_No=number).filter(Date=date).update(Attendance_Time=att_value_orig + change_value)

            ProductionLineAttendanceFact.objects.filter(Date=date).update(AluMskAssembly=F('AluMskAssembly') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(All=F('All') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(Assembly=F('Assembly') + change_value)
        if att[0]['CC'] in ['40602200.0', '40602210.0', '40602220.0', '40602230.0', '40602240.0', '40602250.0']:
            # ScAssembly = ScAssembly + row["AttendanceTime"]
            DailyAttendanceAssFact.objects.filter(Pers_No=number).filter(Date=date).update(
                Attendance_Time=att_value_orig + change_value)

            ProductionLineAttendanceFact.objects.filter(Date=date).update(
                ScAssembly=F('ScAssembly') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(All=F('All') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(Assembly=F('Assembly') + change_value)
        if att[0]['CC'] in ['40602300.0', '40602310.0', '40602320.0', '40602330.0', '40602340.0', '40602150.0']:
            # ShAssembly = ShAssembly + row["AttendanceTime"]
            DailyAttendanceAssFact.objects.filter(Pers_No=number).filter(Date=date).update(
                Attendance_Time=att_value_orig + change_value)

            ProductionLineAttendanceFact.objects.filter(Date=date).update(
                ShAssembly=F('ShAssembly') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(All=F('All') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(Assembly=F('Assembly') + change_value)
        if att[0]['CC'] in ['40602400.0', '40602410.0', '40602420.0', '40602430.0', '40602440.0', '40602450.0']:
            # ScrAssembly = ScrAssembly + row["AttendanceTime"]
            DailyAttendanceAssFact.objects.filter(Pers_No=number).filter(Date=date).update(
                Attendance_Time=att_value_orig + change_value)

            ProductionLineAttendanceFact.objects.filter(Date=date).update(
                ScrAssembly=F('ScrAssembly') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(All=F('All') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(Assembly=F('Assembly') + change_value)

        return Response(json.dumps({"values": "successful"}))


class CncAttendance(APIView):
    def put(self, request, *args, **kwargs):
        number = str(request.data['number'])
        value = float(request.data['value'])
        date = str(request.data['date'])

        att = DailyAttendanceCncFact.objects.filter(Pers_No=number).filter(Date=date).values()

        att_value_orig = att[0]['Attendance_Time']

        change_value = value - att_value_orig

        if att[0]['Description'] in ['40602010.0', '40602040.0', '40602020.0', '40602030.0', '40602050.0']:
            change_value = value - att_value_orig

            att = DailyAttendanceCncFact.objects.filter(Pers_No=number).filter(Date=date).update(Attendance_Time=att_value_orig + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(Cnc=F('Cnc') + change_value)
            ProductionLineAttendanceFact.objects.filter(Date=date).update(All=F('All') + change_value)

        return Response(json.dumps({"values": "successful"}))

