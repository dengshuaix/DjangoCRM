from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import reverse, HttpResponse, redirect
from django.conf import settings
import re
from crm import models

class RbacMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        # 获取当前访问的地址
        url = request.path_info
        # print('这是请求的路径')
        # print(url)

        request.current_menu_id = None
        request.breadcrumb_list = [{'title': '首页', 'url': '/crm/index/'}, ]
        # 白名单
        for i in settings.WHITE_LIST:
            if re.match(i, url):
                return

        # 登陆状态的校验
        is_login = request.session.get('is_login')
        if not is_login:
            return redirect('crm:login')

        # print(request.session.get('user_id'))
        user_obj = models.UserProfile.objects.filter(pk=request.session.get('user_id')).first()

        request.user_obj = user_obj



        # 免认证的校验
        for i in settings.PASS_AUTH_LIST:
            if re.match(i, url):
                return

        # 获取权限信息
        permissions = request.session.get(settings.PERMISSION_SESSION_KEY)

        # print(permissions)
        # 权限的校验
        for i in permissions.values():
            #  i  权限   父权限   子权限
            if re.match(r'^{}$'.format(i['url']), url):
                id = i.get('id')
                pid = i.get('pid')

                if not pid:
                    # 当前访问的权限是父权限  二级菜单
                    request.current_menu_id = id
                    request.breadcrumb_list.append({'url': i['url'], 'title': i['title']})

                else:
                    # 当前访问的权限是子权限
                    request.current_menu_id = pid

                    # 加父权限的信息
                    p_permission = permissions[i.get('pname')]
                    request.breadcrumb_list.append({'url': p_permission['url'], 'title': p_permission['title']})

                    # 加子权限的信息
                    request.breadcrumb_list.append({'url': i['url'], 'title': i['title']})

                return
        # 拒绝请求
        return HttpResponse('没有访问权限，请联系管理员')
