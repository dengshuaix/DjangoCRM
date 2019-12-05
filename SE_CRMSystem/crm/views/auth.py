# -*-coding:utf-8-*-
# Author:Ds
from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from crm.forms import RegForm, CustomerForm, ConsultRecordForm, EnrollmentFrom
import hashlib
from rbac.service.init_permission import  init_permission

### 登录功能
def login(request):
    error = ''
    if request.method == 'POST':
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        md = hashlib.md5()
        md.update(pwd.encode('utf-8'))
        user_obj = models.UserProfile.objects.filter(username=uname, password=md.hexdigest(), is_active=True).first()
        if not user_obj:
            # 用户名和密码校验失败  跳转到登陆页面
            return render(request, 'login.html', {'error': '用户名或密码错误'})
            # 登陆成功  初始化权限信息
        init_permission(user_obj, request)
        # 重定向去首页
        # print(reverse('crm:index'))
        return redirect(reverse('crm:index'))

    return render(request, 'login.html', {'error': error})


### 注册功能
def register(request):
    reg_obj = RegForm()

    if request.method == 'POST':
        reg_obj = RegForm(request.POST)
        if reg_obj.is_valid():
            print(reg_obj.cleaned_data)  # 需要手动删除 re_password键
            reg_obj.save()  # 直接保存
            return redirect('crm:login')

    return render(request, 'register.html', {'reg_obj': reg_obj})

def index(request):
    return render(request,'index.html')