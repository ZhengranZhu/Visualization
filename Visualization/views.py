from ldap3 import Server, Connection, ALL, NTLM
import datetime
import re
from rest_framework.views import APIView
from rest_framework.response import Response
class operate_AD():
    def __init__(self,Domain,User,Password):
        self.domain=Domain
        self.user=User
        self.pwd=Password
        self.DC=','.join(['DC=' + dc for dc in Domain.split('.')])
        # self.pre = Domain.split('.')[0].upper()
        self.server = Server(self.domain, use_ssl=True,get_info=ALL)
        self.conn = Connection(self.server, user=self.user, password = self.pwd, auto_bind = True,)
        self.u_time=datetime.date.today()

    def Get_All_UserInfo(self,username,password):
        '''
        查询组织下的用户
        org: 组织，格式为：aaa.bbb 即bbb组织下的aaa组织，不包含域地址
        '''
        att_list = ['displayName', 'userPrincipalName', 'userAccountControl', 'sAMAccountName', 'pwdLastSet']
        # org_base = ','.join(['OU=' + ou for ou in org.split('.')]) + ',' + self.DC
        res = self.conn.search(search_base=self.DC, search_filter='(sAMAccountName={accounter})'.format(accounter=username),
                               attributes=att_list, paged_size='50', search_scope='SUBTREE',)
        # print(res)
        if res:
            for each in self.conn.response:
                # print(each['dn'])
                user = []
                if len(each) == 5:
                    user = [each['dn'], each['attributes']['sAMAccountName'], each['attributes']['displayName'],]
                    name=user[2]
                    self.conn2 = Connection(self.server, user=name, password=password, auto_bind=True, )
                    if self.conn2:
                        return name
        else:
            print('查询失败: ', self.conn.result['description'])
            return None

    def Get_All_GroupInfo(self):
        '''
        查询组织下的用户
        org: 组织，格式为：aaa.bbb 即bbb组织下的aaa组织，不包含域地址
        '''

        att_list = ['cn', 'member', 'objectClass', 'userAccountControl','SamAccountName', 'description']
        # org_base = ','.join(['OU=' + ou for ou in org.split('.')]) + ',' + self.DC
        res = self.conn.search(search_base=self.DC, search_filter='(objectclass=group)', attributes=att_list,
                               paged_size='', search_scope='SUBTREE')
        if res:
            namelist = []
            for each in self.conn.response:
                # print(each)
                Group = []
                r='CN=(.*?),OU=(.*?),OU=(.*?),OU=(.*?),OU=(.*?),OU=(.*?),DC=(.*?),DC=(.*?)'
                if len(each) == 5:
                    for member in each['attributes']['member']:
                        group = [each['attributes']['sAMAccountName'], member, self.u_time]
                        if (group[0])=="KPI Visualization":
                            a=re.findall(r,group[1])
                            namelist.append(a[0][0].replace("\\",""))

            return namelist
        else:
            print('查询失败: ', self.conn.result['description'])
            return None

class my_login(APIView):
    def post(self,request):
        username=request.POST['username']
        password=request.POST['password']
        act = operate_AD('bitzer.cn', 's00003', '123,.abc')
        user = act.Get_All_UserInfo(username, password)
        print(user)
        namelist = act.Get_All_GroupInfo()
        print(namelist)
        if user in namelist:
            return Response({"username":username,"state":True, "permission":True})
        else:
            return Response({"username":username,"state":True, "permission":False})


