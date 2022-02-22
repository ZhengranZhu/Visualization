from rest_framework import serializers
from Data_aquisition.models import ManufacturingFact, DailyAttendanceCncFact, DailyAttendanceCncFact

class ManufacturingFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturingFact
        fields = ('SerialNumber', 'MaterialNumber', 'SalesOrderNumber', 'ProductionLine', 'PreassemblyStartTime',
                  'WashingStartTime', 'PackagingStartTime', 'AssThroughputTime', 'CncThroughputTime', 'AllThroughputTime')


class AttendanceAssFactSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyAttendanceCncFact
        fields = "__all__"

class AttendanceCncFactSerializer(serializers.ModelSerializer):


    class Meta:
        model = DailyAttendanceCncFact
        fields = "__all__"

