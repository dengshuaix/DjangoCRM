# -*-coding:utf-8-*-
# Author:Ds
from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from utils.pagetions import Pagetions
from django.views import View
from django.db.models import F, Q
from django.db import transaction
from django.conf import global_settings, settings

class BaseView(View):


    def post(self, request,*args,**kwargs):
        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('无效操作')

        self.choice_id = request.POST.getlist('choice_id')

        ## 反射执行具体的方法
        ret = getattr(self, action)()

        if ret:
            return ret

        return self.get(request,*args,**kwargs)


    def search(self, field_list):
        search = self.request.GET.get('search', '')
        q = Q()
        q.connector = 'OR'  # 设置 类型 或类型

        ## 方式一 直接添加Q对象  关键字
        # q.children.append(Q(qq__contains=search))
        # print(field_list)

        ## 方式二  元组   字符串
        for field in field_list:
            q.children.append(Q(('{}__contains'.format(field), search)))

        return q
