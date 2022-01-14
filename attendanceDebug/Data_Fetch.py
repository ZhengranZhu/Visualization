import xlwings as xw
import pandas as pd
import time,datetime
import numpy as np
import pymssql
import sqlalchemy

class data_fetch():
    def attendace_fetch(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=3)
        Search_date=str(yesterday)
        print(type(Search_date),Search_date)
        pd.set_option('display.max_columns',None)
        pd.set_option('display.max_rows',None)
        app=xw.App(visible=False,add_book=False)
        app.display_alerts=False
        app.screen_updating=False
        wb=app.books.open(r"N:\TAData\Time events-20211221.xls")
        data=app.books[0].sheets[0].range('B5:L2000').value
        pd_data=pd.DataFrame(data,columns=data[0])
        pd_data.set_index("Company ID",inplace=True)
        del pd_data[None]
        del pd_data["Personnel No."]
        # del pd_data["Personnel Number"]
        del pd_data["Name"]
        del pd_data["Org. Unit"]
        del pd_data["Name of Organizational Unit"]
        pd_data.dropna(axis=0,inplace=True)
        pd_data=pd_data.iloc[1:]
        c = pd_data.iloc[pd_data.index.str.startswith("PD")]
        output=pd.DataFrame(c)
        output.drop(output.index[(output["Time Event Type"] == 'Clock-in')])
        output.to_excel('attendance.xlsx')
        wb.close()
        app.quit()
        new=pd.read_excel("attendance.xlsx",index_col=[1],parse_dates=[3], date_parser=lambda x:pd.to_datetime(x,format='%Y-%m-%d'))
        new2=pd.DataFrame(new)
        new2.drop(new2.index[(new2["Time Event Type"] == 'Clock-in') & (new2["Log.date"].astype(str) ==Search_date)],inplace=True)
        new2["Attendance_time"]=0
        new2["State"] = "Normal"
        start_time=0
        for index,row in new2.iterrows():
            common=row["Time"]
            if row["Time Event Type"] == 'Clock-in':
                start_time=common
                if row.Time<=0.271 and row.Time>0.23:
                    new2.loc[new2["Time"]==row["Time"],"Time"]=0.271
                if row.Time<=0.604 and row.Time>0.563:
                    new2.loc[new2["Time"]==row["Time"],"Time"]=0.604
                if row.Time<=0.938 and row.Time>0.896:
                    new2.loc[new2["Time"] == row["Time"],"Time"]=0.938
            if row["Time Event Type"]=='Clock-out':
                # if row.Time <= 0.311 and row.Time > 0.271:
                #     # print(row.Time)
                #     new2.loc[new2["Time"] == row["Time"], "Time"] = 0.271
                # if row.Time <= 0.644 and row.Time > 0.604:
                #     # print(row.Time)
                #     new2.loc[new2["Time"] == row["Time"], "Time"] = 0.604
                # if row.Time <= 0.978 and row.Time > 0.938:
                #     # print(row.Time)
                #     new2.loc[new2["Time"] == row["Time"], "Time"] = 0.938
                attendance = common - start_time
                # print(start_time)
                if attendance<0:
                    attendance=attendance+1
                print(attendance)
                new2.loc[[index], "Attendance_time"]=attendance*24
        new2.reset_index(drop=False,inplace=True)
        new2.columns = ['ProductionLine', 'PersonnelName', 'TimeEventType',"LogDate","LogTime","OrganizationUnit","AttendaceTime","State"]
        new2.to_excel("attendace2.xlsx")
        engine = sqlalchemy.create_engine('mssql+pymssql://s00015:Start123!@10.15.8.42\dw:1433/ThroughPutTime?charset=utf8',)
        new2.to_sql(name='Data_aquisition_attendancefact', con=engine, if_exists='replace', index=False)
        print(new2)
if __name__ == '__main__':
    data_fetch().attendace_fetch()