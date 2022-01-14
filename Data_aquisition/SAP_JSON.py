#import time
import urllib.request, json
import datetime
import pandas as pd
from datetime import datetime, timedelta
import os
from Data_aquisition.models import ManufacturingFact, ErrorSerialNumber, DimProductFamily, DimDate, ProductionOrders

class SAP_quisition():
# this function import CNC production order data into sql server database
    def acquire_CNC_production_order(self):

        production_order = pd.read_html('N:\T1data\e.htm')[0]

        production_order = production_order.drop_duplicates()

        production_order.columns = production_order.iloc[0]

        production_order = production_order[1:]

        production_order['创建时间'] = pd.to_timedelta(production_order['创建时间'])
        production_order['创建日期'] = pd.to_datetime(production_order['创建日期'])
        production_order['DateAndTime'] = production_order['创建日期'] + production_order['创建时间']
        production_order['创建日期'] = production_order['创建日期'].dt.strftime('%Y%m%d')


        for index, row in production_order.iterrows():

            work_order = ProductionOrders(OrderNumber=row['附加编号'], DateAndTime=row['DateAndTime'],
                                          Quantity=row['源目标数量'],
                                          Destination=row['目的地仓位'],
                                          OrderDate=DimDate.objects.get(StartDateKey=row['创建日期']))
            try:
                work_order.save()
            except:
                print('order already exists')
        os.remove('N:\T1data\e.htm')
# this function reads all serial number from various excel sheets
    def acquire_serial_number(self, back_days):

        back_days = back_days
        df = pd.read_excel(r'N:\SN\\2022\alu.xlsx')
        df_SC = pd.read_excel(r'N:\SN\2022\SC.xlsx')
        df_SC = df_SC[['开始日期', '数量', '压缩机起始号', '压缩机结束号']]
        df_SC.dropna(inplace=True)
        df_SH = pd.read_excel(r'N:\SN\2022\SH.xlsx')
        df_SH = df_SH[['quantity', 'SN. start', 'SN. end', 'Start Date']]
        df_SH.dropna(inplace=True)
        df = df[['机器序号        (From S.N. )', '机器序号       (To S.N.)', '    数量     Quantity', '基本开始      Start Date']]
        df.rename(columns={'机器序号        (From S.N. )': "StartSerialNumber", '机器序号       (To S.N.)': "EndSerialNumber", '    数量     Quantity': 'Quantity',
                           '基本开始      Start Date': '开始日期'}, inplace=True)
        df.dropna(inplace=True)
        df.Quantity = df.Quantity.astype(int)
        df_SC['数量'] = df_SC['数量'].astype(int)
        df_SH.quantity = df_SH.quantity.astype(int)

        today_data = df.loc[df['开始日期'] == str(datetime.now().date() - timedelta(back_days))]
        today_data_sc = df_SC.loc[df_SC['开始日期'] == str(datetime.now().date() - timedelta(back_days))]
        today_data_sh = df_SH.loc[df_SH['Start Date'] == str(datetime.now().date() - timedelta(back_days))]


        list_of_serial_number = []
        for index, row in today_data.iterrows():
            serial_number = row['StartSerialNumber']
            list_of_serial_number.append(serial_number)
            for i in range(row['Quantity']-1):
                serial_number += 1
                list_of_serial_number.append(serial_number)
        #
        for index, row in today_data_sc.iterrows():
            serial_number = row['压缩机起始号']
            list_of_serial_number.append(serial_number)
            for i in range(row['数量']-1):
                serial_number += 1
                list_of_serial_number.append(serial_number)

        for index, row in today_data_sh.iterrows():
            serial_number = row['SN. start']
            list_of_serial_number.append(serial_number)
            for i in range(row['quantity']-1):
                serial_number += 1
                list_of_serial_number.append(serial_number)
        print(list_of_serial_number)

        return [str(int(serial)) for serial in list_of_serial_number]


    def SAP_data(self, serial_number):

        # Add the username and password.
        # If we knew the realm, we could use it instead of None.

        link_head = "https://vhbizpfclb.rot.hec.bitzer.biz/sap/opu/odata/sap/ZCDS_MES_VIEW1_CDS/ZCDS_MES_VIEW1(p_sernr='00000000"
        serial_number = serial_number
        link_tail = "')/Set?$top=10&$format=json"
        link = link_head + serial_number + link_tail

        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        # If we knew the realm, we could use it instead of None.
        top_level_url = link
        username = "PP_ODATA_CN"
        password = "b0ZHT?f=6863lATjkHL3"
        password_mgr.add_password(None, top_level_url, username, password)

        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

        # create "opener" (OpenerDirector instance)
        opener = urllib.request.build_opener(handler)

        # use the opener to fetch a URL
        opener.open(top_level_url)

        # Install the opener.
        # Now all calls to urllib.request.urlopen use our opener.
        urllib.request.install_opener(opener)

        with urllib.request.urlopen(top_level_url) as response:
            html = response.read()

        sap_data = json.loads(html)

        return sap_data['d']['results']


    def acquire_sap_data(self, sap_data, serial_number):
        serial_number = serial_number
        sap_data = sap_data
        preassembly_order_number = sap_data[0]["AdditionalFieldData"]
        manufacturing = {'SerialNumber': '', 'MaterialNumber': '', 'SalesOrderNumber': '', 'Plant': '',
                         'ProductionLine': '',
                         'PreassemblyStartTime': '', 'WashingStartTime': '', 'PackagingStartTime': '',
                         'PreassemblyStartDateKey': '',
                         'WashingStartDateKey': '', 'PackagingStartDateKey': '', 'ProductFamilyKey': '',
                         'AllThroughputTime': '',
                         'AssThroughputTime': '', 'CncThroughputTime': ''}

        CS = ['CSK61', 'CSK71', 'CSH65', 'CSH75', 'CSH85', 'CSH95', 'CSW65', 'CSW75', 'CSW85',
              'CSW95']
        HS = ['HS74', 'HS85']
        cylinder_F = ['2FC', '6FC', '4FS']
        BIFA = ['4FC']
        MSK = ['CSA3']
        CE1S = ['CE1S']
        SH = ['CE2S', 'CE3S', 'CE4', 'CE4S', 'B4', 'BS4', 'BE5', 'BS5', 'BE6', 'BS6']
        HT = ['CE2HT', 'CE3HT', 'CE4HT']
        Variospeed = ['CE2F', 'CE2SF', 'CE3F', 'CE4F']
        for item in sap_data:
            manufacturing['SerialNumber'] = serial_number
            manufacturing['MaterialNumber'] = item['MaterialNumber']
            manufacturing['SalesOrderNumber'] = item['SalesOrderNumber']
            manufacturing['Plant'] = item['Plant']
            manufacturing['ProductFamilyKey'] = item['Family']
            if item['Family'] in CS or item['Family'] in HS and item['ActivityNumber'] == '0030':
                manufacturing['ProductionLine'] = 'SC'
                if item['ActivityNumber'] == '0030':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0190':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in HS:
                manufacturing['ProductionLine'] = 'SC'
                if item['ActivityNumber'] == '0040':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0230':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())

                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in BIFA:
                manufacturing['ProductionLine'] = 'ALU&MSK'
                if item['ActivityNumber'] == '0080':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0240':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in MSK:
                manufacturing['ProductionLine'] = 'ALU&MSK'
                if item['ActivityNumber'] == '0100':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0280':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in CE1S:
                manufacturing['ProductionLine'] = 'SH'
                if item['ActivityNumber'] == '0040':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0200':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in SH:
                manufacturing['ProductionLine'] = 'SH'
                if item['ActivityNumber'] == '0040':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0180':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in HT:
                manufacturing['ProductionLine'] = 'SH'
                if item['ActivityNumber'] == '0040':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')
                elif item['ActivityNumber'] == '0180':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')
            elif item['Family'] in cylinder_F:
                manufacturing['ProductionLine'] = 'ALU&MSK'
                if item['ActivityNumber'] == '0040':
                    manufacturing['WashingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['WashingStartDateKey'] = datetime.strftime(
                        manufacturing['WashingStartTime'].date(), '%Y%m%d')

                elif item['ActivityNumber'] == '0170':
                    manufacturing['PackagingStartTime'] = datetime.combine(
                        datetime.fromtimestamp(int(item['EntryDateOfConfirmation'][6:16])).date(),
                        datetime.strptime(
                            item['ConfirmationEntryTime'][2:4] + ':' + item['ConfirmationEntryTime'][5:7] + ':' +
                            item['ConfirmationEntryTime'][8:10], '%H:%M:%S').time())
                    manufacturing['PackagingStartDateKey'] = datetime.strftime(
                        manufacturing['PackagingStartTime'].date(), '%Y%m%d')


        manufacturing['AssThroughputTime'] = round((manufacturing['PackagingStartTime'] - manufacturing['WashingStartTime']).total_seconds()/60, 2)
        manufacturing['PreassemblyStartTime'] = SAP_quisition().acqurie_CNC_TO_time(preassembly_order_number=preassembly_order_number)
        #
        manufacturing['PreassemblyStartDateKey'] = datetime.strftime(
                         manufacturing['PreassemblyStartTime'].date(), '%Y%m%d')
        manufacturing['CncThroughputTime'] = round((manufacturing['WashingStartTime'] - manufacturing['PreassemblyStartTime']).total_seconds()/60, 2)
        manufacturing['AllThroughputTime'] = round(
            (manufacturing['PackagingStartTime'] - manufacturing['PreassemblyStartTime']).total_seconds()/60, 2)
        return manufacturing


    def acqurie_CNC_TO_time(self, preassembly_order_number):

        preassembly_order_number = preassembly_order_number
        matching_p_order = ProductionOrders.objects.filter(OrderNumber=preassembly_order_number).values()
        if not matching_p_order:
            date_time = None
        else:
            date_time = matching_p_order[0]['DateAndTime']
        # production_order = pd.read_html('N:\T1data\order.htm')[0]
        #
        # production_order = production_order.drop_duplicates()
        # production_order.columns = production_order.iloc[0]
        #
        #
        # production_order = production_order[1:]
        # date_of_order = production_order[production_order['附加编号'] == preassembly_order_number]['创建日期']
        # time_of_order = production_order[production_order['附加编号'] == preassembly_order_number]['创建时间']
        # date_time = str(date_of_order.tolist()[0]) + ' ' + str(time_of_order.tolist()[0])

        return date_time.replace(tzinfo=None)

    def load_database(self, serial_number_list, errored_serial_number_list):
        errored_serial_number_list = errored_serial_number_list
        serial_number_list = serial_number_list
        serial_number_list = serial_number_list + errored_serial_number_list

        for serial_number in serial_number_list:
            sap_row_data = SAP_quisition().SAP_data(serial_number)
            try:
                manufacturing_data = SAP_quisition().acquire_sap_data(sap_data=sap_row_data,
                                                                      serial_number=serial_number)

                manufacturing = ManufacturingFact(SerialNumber=manufacturing_data['SerialNumber'],
                                                  MaterialNumber=manufacturing_data['MaterialNumber'], SalesOrderNumber=
                                                  manufacturing_data['SalesOrderNumber'],
                                                  Plant=manufacturing_data['Plant'],
                                                  ProductionLine=manufacturing_data['ProductionLine'],
                                                  PreassemblyStartDateKey=DimDate.objects.get(
                                                      StartDateKey=manufacturing_data['PreassemblyStartDateKey']),
                                                  PreassemblyStartTime=manufacturing_data['PreassemblyStartTime'],
                                                  WashingStartTime=manufacturing_data['WashingStartTime'],
                                                  WashingStartDateKey=DimDate.objects.get(
                                                      StartDateKey=manufacturing_data['WashingStartDateKey']),
                                                  PackagingStartTime=manufacturing_data['PackagingStartTime'],
                                                  PackagingStartDateKey=DimDate.objects.get(
                                                      StartDateKey=manufacturing_data['PackagingStartDateKey']),
                                                  ProductFamilyKey=DimProductFamily.objects.get(
                                                      ProductFamilyKey=manufacturing_data['ProductFamilyKey']),
                                                  AllThroughputTime=manufacturing_data['AllThroughputTime'],
                                                  CncThroughputTime=manufacturing_data['CncThroughputTime'],
                                                  AssThroughputTime=manufacturing_data['AssThroughputTime']

                                                  )
                manufacturing.save()
                print('saved successfully')
            except:
                if not ManufacturingFact.objects.filter(SerialNumber=serial_number).exists():
                    exception = ErrorSerialNumber(SerialNumber=serial_number)
                    exception.save()

    def update_from_errored(self):
        # This function receivs the those serial number in iserrored table and reload it from SAP database
        error_serial_number = ErrorSerialNumber().objects

        return None

    def load_cnc_order(self):
        return None


    def reload_errored_serial_number(self):
        query_set = ErrorSerialNumber.objects.values('SerialNumber')

        errored_serial_number_list = []
        print(query_set)

        for item in query_set:
            print(item)
            if not ManufacturingFact.objects.filter(SerialNumber=item['SerialNumber']).exists():
                print('11554')
                errored_serial_number_list.append(item['SerialNumber'])
            else:
                pass
        print(errored_serial_number_list)
        ErrorSerialNumber.objects.all().delete()
        return errored_serial_number_list

if __name__ == '__main__':
    #SAP_quisition().acquire_CNC_production_order()
    #serial_number_list = SAP_quisition().acquire_serial_number(back_days=0)
    # print(serial_number_list)
    #
    SAP_quisition().acquire_CNC_production_order()







    # a = SAP_quisition().acquire_sap_data(m, '1901207778')
    # print(a)
    #SAP_quisition().load_database(['1901207778'])

    # print(m)















