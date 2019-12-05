# -*-coding:utf-8-*-
# Author:Ds

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import reverse,redirect
from crm import models
class MyMiddleware(MiddlewareMixin):

    def process_request(self,request):

        ###  url  白名单
        urls=[reverse('crm:login'),reverse('crm:register')]

        if request.path_info in urls:
            return

        if request.path_info.startswith('/admin/'):
            return

        obj=models.UserProfile.objects.filter(pk=request.session.get('user_id')).first()

        if not obj or request.session.get('is_login')!='1':
            return redirect('crm:login')

        request.user_obj=obj
