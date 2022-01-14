from Data_aquisition.models import ManufacturingFact, DimProductFamily, DimDate, DimProductFamily, ProductionOrders, ProductionLineAttendanceFact
import pandas as pd
from django.db.models import Avg
from datetime import datetime
from calendar import monthrange


def allDays(y, m):
    return ['{:04d}{:02d}{:02d}'.format(y, m, d) for d in range(1, monthrange(y, m)[1] + 1)]
def create_date_table(keyname, start='20210101', end='20501231'):
    df = pd.DataFrame({keyname: pd.date_range(start, end)})
    df["CalendarYear"] = df[keyname].dt.year
    df["MonthOfYear"] = df[keyname].dt.month
    df['WeekOfYear'] = df[keyname].dt.isocalendar().week
    df["MonthName"] = df[keyname].dt.month_name()
    df["DayOfMonth"] = df[keyname].dt.daysinmonth
    df["DayOfWeek"] = df[keyname].dt.dayofweek + 1
    df["DayName"] = df[keyname].dt.day_name()
    df["FiscalYear"] = df[keyname].dt.year
    df["FiscalQuarter"] = df[keyname].dt.quarter
    df[keyname] = df[keyname].dt.strftime('%Y%m%d')
    return df


df_testing = create_date_table(keyname="TestingStartDateKey")

df_washing = create_date_table(keyname="StartDateKey")
#print(df_testing)
# for index, row in df.iterrows():
#     print( row.MonthName, row.DayOfMonth, row.DayOfWeek, row.DayName, row.FiscalYear, row.FiscalQuarter)

def load_dim_Washing(df_washing):
    for index, row in df_washing.iterrows():
        washing = DimDate(StartDateKey=row.StartDateKey, CalendarYear=row.CalendarYear, MonthOfYear=
                                 row.MonthOfYear, WeekOfYear=row.WeekOfYear, MonthName=row.MonthName, DayOfMonth=row.DayOfMonth,
                                 DayOfWeek=row.DayOfWeek, DayName=row.DayName, FiscalYear=row.FiscalYear, FiscalQuarter=
                                 row.FiscalQuarter)

        washing.save()


#load_dim_Washing(df_washing)
#load_dim_Testing(df_testing)
#
# manufacture = ManufacturingFact(SerialNumber='5452278956', ProductFamilyKey=DimProductFamily.objects.get(ProductFamilyKey='4FC'), MaterialNumber='3994555548',
#                                 SalesOrderNumber='1236987545', Plant='BRT', ProductionLine='Alu', PreassemblyStartDateKey=DimDate.objects.get(StartDateKey='2021-11-28'), PreassemblyStartTime=pd.to_datetime('20211128205945'),
#                                 PackagingStartDateKey=DimDate.objects.get(StartDateKey='2021-11-28'), PackagingStartTime=pd.to_datetime('20211128215430'), WashingStartDateKey=
#                                 DimDate.objects.get(StartDateKey='2021-11-28'), WashingStartTime=pd.to_datetime('20211128224554'),
#                                AllThroughputTime=80, CncThroughputTime=60, AssThroughputTime=50)
# manufacture.save()
#
# product_family = DimProductFamily(ProductFamilyKey='2', ProductDescriptionEn='abc')
# product_family.save()
# product_type = DimProductType(ProductTypeKey='2', ProductTypeDescriptionEn='dbe')
# product_type.save()
#
#
#
# throughput_time = [0]*12
# date_list = list(range(2017, 2029))
#
# query_set = ManufacturingFact.objects.values('TestingStartDateKey__CalendarYear').order_by('TestingStartDateKey__CalendarYear')\
#                     .annotate(average_throughputTime=Avg('AllThroughputTime'))
#
#
#
#
#
# for item in query_set:
#     if item['TestingStartDateKey__CalendarYear'] in date_list:
#     #date_list.append(item['TestingStartDateKey'])
#
#         throughput_time[date_list.index(item['TestingStartDateKey__CalendarYear'])] = item['average_throughputTime']
#
# print(throughput_time, date_list)
# #



# CS = ['CSK61', 'CSK71', 'CSH65.3', 'CSH75.3', 'CSH85.3', 'CSH95.3', 'CSW65.3', 'CSW75.3', 'CSW85.3',
#               'CSW95.3']
# HS = ['HS74', 'HS85']
# cylinder_F = ['2FC', '6FC', '4FS']
BIFA = ['4FC']
# MSK = ['CSA3']
# CE1S = ['CE1S']
# SH = ['CE2S', 'CE3S', 'CE4', 'CE4S', 'B4', 'BS4', 'BE5', 'BS5', 'BE6', 'BS6']

#     row = DimProductFamily(ProductFamilyKey=item, ProductDescriptionEn='ALU&MSK', StandardManufacturingTime=63.7, CncStandardTime=15.5)
#     row.save()



# df = pd.read_excel("//10.15.8.42/TAData/Time events-20211221.xls")
# df.head()
# running_time = DimProductFamily.
def acquire_CNC_production_order():

    production_order = pd.read_html('N:\T1data\e.htm')[0]

    production_order = production_order.drop_duplicates()

    production_order.columns = production_order.iloc[0]

    production_order = production_order[1:]

    production_order['创建时间'] = pd.to_timedelta(production_order['创建时间'])
    production_order['创建日期'] = pd.to_datetime(production_order['创建日期'])
    production_order['DateAndTime'] = production_order['创建日期'] + production_order['创建时间']
    production_order['创建日期'] = production_order['创建日期'].dt.strftime('%Y%m%d')
    print(production_order)

    for index, row in production_order.iterrows():

        work_order = ProductionOrders(OrderNumber=row['附加编号'], DateAndTime=row['DateAndTime'], Quantity=row['源目标数量'],
                                      Destination=row['目的地仓位'], OrderDate=DimDate.objects.get(StartDateKey=row['创建日期']))
        try:
            work_order.save()
        except:
            print('order already exists')

this_month = datetime.now().month
this_year = datetime.now().year
# from django.db.models import Avg, Count, Sum
# #acquire_CNC_production_order()
# query_set = ManufacturingFact.objects.filter(PackagingStartDateKey__MonthOfYear=12).values(
#             'ProductFamilyKey__ProductDescriptionEn', 'PackagingStartDateKey').annotate(
#             total_cnc_hours=Sum('ProductFamilyKey__CncStandardTime'), total_ass_hours=Sum('ProductFamilyKey__StandardManufacturingTime')).order_by('ProductFamilyKey__ProductDescriptionEn', 'PackagingStartDateKey')
# attendance_this_month = ProductionLineAttendanceFact.objects.filter(Date__MonthOfYear=12).values('All', 'Date')
# print(query_set)
#
# a = allDays(this_year, this_month)
# productivity_monthly = [0]*len(a)
# for item in query_set:
#     for attendance in attendance_this_month:
#         if item['PackagingStartDateKey'] == attendance['Date']:
#             productivity_monthly[a.index(item['PackagingStartDateKey'])] = item['total_cnc_hours'] + item['total_ass_hours']
# print(productivity_monthly)

manufatruing = ManufacturingFact.objects.filter(ProductionLine='ALU&MSK').values('SerialNumber','AllThroughputTime', 'PackagingStartTime').order_by('-PackagingStartTime')[:10]

print(manufatruing)

# for item in query_set:
#     family_hours['hours'] = item['dcount'] * (
#                 item['ProductFamilyKey__CncStandardTime'] + item['ProductFamilyKey__StandardManufacturingTime'])
#     family_hours['Date'] = item['PackagingStartDateKey']
#     family_hours['Line'] = item['ProductFamilyKey__ProductDescriptionEn']
#     family_hours['Family'] = item['ProductFamilyKey']
# #     standard_working_hours.append(family_hours)
#
# print(standard_working_hours)


