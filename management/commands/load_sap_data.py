from django.core.management.base import BaseCommand, CommandError
import urllib.request, json
import datetime
import pandas as pd
from datetime import datetime, timedelta
import os
from Data_aquisition.models import ManufacturingFact, ErrorSerialNumber, DimProductFamily, DimDate, ProductionOrders


# class Command(BaseCommand):
#     help = 'this helps to load sap data to database every certian period'