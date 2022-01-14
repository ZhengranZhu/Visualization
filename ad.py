from Visualization.settings import ldapserver,mail_postfix ,se_dn,se_pw,base_dn,attrs,filter
import ldap
# class my_login(APIView):
#     def post(self,request):
#         context = {}
#         username=request.POST['username']
#         password=request.POST['password']
#         a = myldapBackend()
#         print(username,password)
#         user = a.authenticate(username=username, password=password)
#         if user:
#             context = {'state': True}
#             return Response(context,status=status.HTTP_200_OK)
#         else:
#             context = {'state': False}
#             return Response(context,status=status.HTTP_404_NOT_FOUND)

class myldapBackend():
    def authenticate(self, username=None, password=None):
        if len(password) == 0:
            return None
        con = ldap.initialize(ldapserver)

        r1 = con.simple_bind_s(se_dn, se_pw)
        print(r1)
        search_result = con.search_s(base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
        print(search_result)
        for i in search_result:
            if i[1]['cn'][0].decode() == username:
                x = i[1]['department'][0].decode()
                dn = i[0]
                result = con.simple_bind_s(dn, password)
                print(result)
                break
            else:
                pass
        if result:
            return True
        else:
            return False

if __name__ == '__main__':
    a=myldapBackend().authenticate(username="Pan,wenfang",password="welcome2Bitzer#")
    print(a)