#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from Data_aquisition import SAP_JSON
from multiprocessing import Process
import time
import threading
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visualization.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def data_aquisition():
    while True:
        try:
            SAP_JSON.SAP_quisition().acquire_CNC_production_order()
        except:
            pass
        errored_serial_number_list = SAP_JSON.SAP_quisition().reload_errored_serial_number()
        SAP_JSON.SAP_quisition().load_database(errored_serial_number_list)
        serial_number_list = SAP_JSON.SAP_quisition().acquire_serial_number(back_days=1)
        SAP_JSON.SAP_quisition().load_database(serial_number_list)
        time.sleep(3600*3)



if __name__ == '__main__':
    # P1=Process(target=main)
    # P2=Process(target=data_aquisition)
    # P1.start()
    # P2.start()

    # th1= threading.Thread(target=main)
    # th2 = threading.Thread(target=data_aquisition)
    # # # th1.start()
    # th2.start()
    # # th1.join()
    main()
    # th2.join()



