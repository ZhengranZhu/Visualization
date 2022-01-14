from django.db import models

import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visualization.settings')

django.setup()
#Create your models here.
from datetime import datetime

class DimDate(models.Model):
    StartDateKey = models.CharField(max_length=10, unique=True)
    CalendarYear = models.IntegerField()
    MonthOfYear = models.IntegerField()
    WeekOfYear = models.IntegerField(null=True)
    MonthName = models.CharField(max_length=20)
    DayOfMonth = models.IntegerField()
    DayOfWeek = models.IntegerField()
    DayName = models.CharField(max_length=20)
    FiscalYear = models.IntegerField()
    FiscalQuarter = models.IntegerField()

    def __str__(self):
        return self.StartDateKey



class DimProductFamily(models.Model):
    ProductFamilyKey = models.CharField(max_length=20, unique=True)
    ProductDescriptionEn = models.CharField(max_length=500, null=True)
    StandardManufacturingTime = models.FloatField(null=True)
    CncStandardTime = models.FloatField(null=True)

    def __str__(self):
        return self.ProductFamilyKey


class ManufacturingFact(models.Model):
    SerialNumber = models.CharField(max_length=20, unique=True)
    ProductFamilyKey = models.ForeignKey(DimProductFamily, to_field='ProductFamilyKey', related_name='Family', on_delete=models.CASCADE, default='')
    MaterialNumber = models.CharField(max_length=10, unique=False, null=True)
    SalesOrderNumber = models.CharField(max_length=10, unique=False, null=True)
    Plant = models.CharField(max_length=10, null=True)
    ProductionLine = models.CharField(max_length=10, null=True)

    PreassemblyStartDateKey = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='Preassembly',
                                                default='', on_delete=models.CASCADE)
    PreassemblyStartTime = models.DateTimeField()
    WashingStartDateKey = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='Washing',
                                            default='', on_delete=models.CASCADE)
    WashingStartTime = models.DateTimeField()
    PackagingStartDateKey = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='Testing',
                                            default='', on_delete=models.CASCADE)
    PackagingStartTime = models.DateTimeField()

    CncThroughputTime = models.FloatField(null=True)
    AssThroughputTime = models.FloatField(null=True)
    AllThroughputTime = models.FloatField(null=True)




    def __str__(self):
        return self.SerialNumber
#
class DailyAttendanceAssFact(models.Model):
    Pers_No = models.CharField(max_length=50, null=True)
    Name = models.CharField(max_length=50, null=True)
    CC = models.CharField(max_length=100, null=True)
    Description = models.CharField(max_length=100)
    Date = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='AttendancePerson', default='', on_delete=models.CASCADE)
    Attendance_Time = models.FloatField(null=True)

    class Meta:
        unique_together = ('Pers_No', 'Date')

class DailyAttendanceCncFact(models.Model):
    Pers_No = models.CharField(max_length=50, null=True)
    Name = models.CharField(max_length=50, null=True)
    CC = models.CharField(max_length=100, null=True)
    Description = models.CharField(max_length=100)
    Date = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='AttendanceCNCPerson', default='', on_delete=models.CASCADE)
    Attendance_Time = models.FloatField(null=True)

    class Meta:
        unique_together = ('Pers_No', 'Date')

class ErrorSerialNumber(models.Model):
    SerialNumber = models.CharField(max_length=20)
    IsCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.SerialNumber


class ProductionLineAttendanceFact(models.Model):
    ShAssembly = models.FloatField()
    ScAssembly = models.FloatField()
    ScrAssembly = models.FloatField()
    AluMskAssembly = models.FloatField()
    Cnc = models.FloatField()
    Assembly = models.FloatField()
    All = models.FloatField()
    Date = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='AttendanceAssPerson', default='', on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.Date

class ProductionOrders(models.Model):
    OrderNumber = models.CharField(primary_key=True, max_length=12)
    OrderDate = models.ForeignKey(DimDate, to_field='StartDateKey', related_name='CncOrder', default='', on_delete=models.CASCADE)
    DateAndTime = models.DateTimeField()
    Quantity = models.IntegerField()
    Destination = models.CharField(max_length=30)

    def __str__(self):
        return self.OrderNumber

#
class TemperorayProductivityTable(models.Model):
    Date = models.CharField(max_length=8, primary_key=True)
    ALUMSK = models.FloatField()
    SH = models.FloatField()
    SC = models.FloatField()
    SCR = models.FloatField()

    def __str__(self):
        return self.Date











