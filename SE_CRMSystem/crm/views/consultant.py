# -*-coding:utf-8-*-
# Author:Ds

from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from django.http import JsonResponse
from crm.forms import RegForm, CustomerForm, ConsultRecordForm, EnrollmentFrom
from utils.pagetions import Pagetions
from django.views import View
from django.db.models import F, Q
from django.db import transaction
from SE_CRMSystem.settings import MAX_CUSTOMER_NUM
from django.conf import global_settings,settings

### 展示客户信息 (包含分页的功能)

class Customer_list(View):
    def get(self, request):
        # print(request.GET, type(request.GET))
        # print(request.GET)
        # print(request.GET.urlencode(), type(request.GET.urlencode()))  ###

        # 模糊查询方法
        q = self.search(['qq', 'qq_name', 'name', 'phone'])

        if request.path_info == reverse('crm:customer_list'):
            all_customers = models.Customer.objects.filter(q, consultant_id__isnull=True).order_by(
                'status').reverse()

        else:
            all_customers = models.Customer.objects.filter(q, consultant=request.user_obj).order_by('status')

        curPage = request.GET.get('page')

        page_customer_obj = Pagetions(curPage, len(all_customers), request.GET.copy(), page_nums=3, max_show=7)

        return render(request, 'consultant/customer_list.html',
                      {'all_customers': all_customers[page_customer_obj.start:page_customer_obj.end],
                       'page_html': page_customer_obj.page_html()})

    def post(self, request):
        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('无效操作')

        self.choice_id = request.POST.getlist('choice_id')

        ## 反射执行具体的方法
        ret=getattr(self, action)()

        if ret:
            return ret

        return self.get(request)

    def mutli_apply(self):
        ### 公户转私户
        # 方式一
        # 通过 客户关联销售
        my_customer_count=models.Customer.objects.filter(consultant=self.request.user_obj).count()
        ## 判断私户上限
        if my_customer_count+len(self.choice_id)>settings.MAX_CUSTOMER_NUM:
            extra=int(settings.MAX_CUSTOMER_NUM) - int(my_customer_count)
            print(extra)
            return HttpResponse(f'做人不能太贪心,给别人留一点,您的剩余名额还有{extra}')

        try:
            with transaction.atomic():
                ## 添加  行级锁 select_for_update()  ,对条件进行进一步限制.
                queryset=models.Customer.objects.filter(pk__in=self.choice_id,consultant=None).select_for_update()
                # 当查询出来的数据 , 和提交的数据量一致 . 才进行更新
                if len(self.choice_id)==queryset.count():
                    queryset.update(consultant=self.request.user_obj)
                else:
                    return HttpResponse('手速太慢了,更改无效')

        except Exception as e:
            print(e)
        # 方式二
        # 通过销售添加客户
        # self.request.user_obj.customers.add(*models.Customer.objects.filter(pk__in=self.choice_id))

    def mutli_pub(self):
        ### 私户转公户
        # 方式一
        # models.Customer.objects.filter(pk__in=self.choice_id).update(consultant=None)
        # 方式二
        change_user = models.Customer.objects.filter(pk__in=self.choice_id)
        self.request.user_obj.customers.remove(*change_user)

    def search(self, field_list):
        search = self.request.GET.get('search', '')
        q = Q()
        q.connector = 'OR'  # 设置 类型 或类型

        ## 方式一 直接添加Q对象  关键字
        q.children.append(Q(qq__contains=search))

        ## 方式二  元组   字符串
        for field in field_list:
            q.children.append(Q(('{}__contains'.format(field), search)))

        return q


### 添加客户信息
def customer_add(request):
    customer_form_obj = CustomerForm(request)
    if request.method == 'POST':
        customer_form_obj = CustomerForm(request.POST)
        if customer_form_obj.is_valid():
            customer_form_obj.save()
            return redirect('crm:customer_list')

    return render(request, 'consultant/customer_add.html', {'customer_form_obj': customer_form_obj})


### 编辑客户信息
def customer_edit(request, pk):
    cur_obj = models.Customer.objects.filter(pk=pk).first()
    customer_form_obj = CustomerForm(request, instance=cur_obj)
    if request.method == 'POST':
        customer_form_obj = CustomerForm(request.POST, instance=cur_obj)
        if customer_form_obj.is_valid():
            customer_form_obj.save()
            return redirect('crm:customer_list')
    return render(request, 'consultant/customer_edit.html', {'customer_form_obj': customer_form_obj})


### 客户信息新增和编辑
def customer_change(request, pk=None):
    cur_obj = models.Customer.objects.filter(pk=pk).first()
    customer_form_obj = CustomerForm(request, instance=cur_obj)
    if request.method == 'POST':
        customer_form_obj = CustomerForm(request, request.POST, instance=cur_obj)
        if customer_form_obj.is_valid():
            customer_form_obj.save()

            ## next 参数
            next = request.GET.get('next')
            if next:
                return redirect(next)

            return redirect('crm:customer_list')
    title = '添加客户' if pk else '编辑客户'
    return render(request, 'consultant/customer_change.html', {'customer_form_obj': customer_form_obj, 'title': title})


# def customer_filed_search(request):
#     if request.method == 'POST':
#         content = request.POST.get('search')
#
#     customer_form_obj = CustomerForm()
#     if request.path_info == reverse('crm:customer_list'):
#         all_customers = models.Customer.objects.filter(
#             Q(consultant_id__isnull=True) & Q(qq__contains=content)).reverse().order_by(
#             'status').reverse()
#     else:
#         all_customers = models.Customer.objects.filter(
#             Q(consultant=request.user_obj) & Q(qq__contains=content)).order_by('status')
#
#     curPage = request.GET.get('page')
#     page_customer_obj = Pagetions(curPage, len(all_customers), page_nums=10, max_show=7)
#     return render(request, 'customer_list.html',
#                   {'all_customers': all_customers[page_customer_obj.start:page_customer_obj.end],
#                    'page_html': page_customer_obj.page_html(), 'customer_form_obj': customer_form_obj})


####### 跟进记录表 展示

class ConsultRecord_list(View):
    def get(self, request, customer_id=None, *args, **kwargs):
        curPage = request.GET.get('page')
        if customer_id:
            print(customer_id)
            all_consulrecord = models.ConsultRecord.objects.filter(customer__id=customer_id,
                                                                   customer__consultant=request.user_obj,
                                                                   delete_status=False)
            print(all_consulrecord)
        else:
            all_consulrecord = models.ConsultRecord.objects.filter(consultant=request.user_obj, delete_status=False)
        page_conrec_obj = Pagetions(curPage, all_consulrecord.count(), request.GET.copy(), page_nums=3, max_show=5)

        return render(request, 'consultant/consultRecord_list.html',
                      {'all_consulrecord': all_consulrecord.order_by('-date')[
                                           page_conrec_obj.start:page_conrec_obj.end],
                       'page_html': page_conrec_obj.page_html})

    def post(self, request):
        pass

    def search(self, field_list):
        search = self.request.GET.get('search', '')
        q = Q()
        q.connector = 'OR'  # 设置 类型 或类型

        ## 方式一 直接添加Q对象  关键字
        # q.children.append(Q(qq__contains=search))

        ## 方式二  元组   字符串
        for field in field_list:
            q.children.append(Q(('{}__contains'.format(field), search)))

        return q


##### 跟进记录表添加和编辑
def consultrecord_change(request, pk=None):
    conrec_obj = models.ConsultRecord.objects.filter(pk=pk).first()

    conrec_form_obj = ConsultRecordForm(request, instance=conrec_obj)

    if request.method == 'POST':
        conrec_form_obj = ConsultRecordForm(request, request.POST, instance=conrec_obj)

        if conrec_form_obj.is_valid():
            conrec_form_obj.save()

            ## next 参数
            next = request.GET.get('next')
            if next:
                return redirect(next)

            return redirect('crm:consultrecord_list')
    title = '添加跟进记录' if not pk else '编辑跟进记录'

    return render(request, 'form.html', {'form_obj': conrec_form_obj, 'title': title})


###  报名表 展示
class Enrollment_list(View):
    def get(self, request, customer_id=None):
        curPage = request.GET.get('page')

        if customer_id:
            all_enrollment = models.Enrollment.objects.filter(customer_id=customer_id)
        else:
            all_enrollment = models.Enrollment.objects.filter(customer__consultant=request.user_obj)

        page_conrec_obj = Pagetions(curPage, all_enrollment.count(), request.GET.copy(), page_nums=3, max_show=5)

        return render(request, 'consultant/enrollment_list.html',
                      {'all_enrollment': all_enrollment[page_conrec_obj.start:page_conrec_obj.end],
                       'page_html': page_conrec_obj.page_html})

    def post(self, request):
        pass

    def search(self, field_list):
        search = self.request.GET.get('search', '')
        q = Q()
        q.connector = 'OR'  # 设置 类型 或类型

        ## 方式二  元组   字符串
        for field in field_list:
            q.children.append(Q(('{}__contains'.format(field), search)))

        return q

###  报名表 新增和编辑
def enrollment_change(request, pk=None, customer_id=None):
    ### 生成Enrollment对象, 前者携带客户的ID ,后者是根据PK主键查询.
    obj = models.Enrollment(customer_id=customer_id) if customer_id else models.Enrollment.objects.filter(pk=pk).first()


    # print('执行到此处')
    # print(obj)

    # form_obj=EnrollmentFrom(customer_id,instance=obj)
    form_obj = EnrollmentFrom(instance=obj)

    if request.method == 'POST':


        form_obj = EnrollmentFrom(request.POST, instance=obj)

        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            # print('next的参数:',next)
            if next:
                return redirect(next)
            return redirect('crm:enrollment_list')

    title = '新增报名表' if customer_id else '编辑报名表'
    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})




### ajax提交客户数据
def customer_add_ajax(request):
    if request.method == 'POST':

        customer_form_obj = CustomerForm(request.POST)
        if customer_form_obj.is_valid():
            customer_form_obj.save()
            return JsonResponse({'status': True})


### (自己写的demo) 展示用户信息(CBV)
class Customers(View):
    def get(self, request):
        customers_obj = models.Customer.objects.all()
        return render(request, 'consultant/customer.html', {'customers_obj': customers_obj})


### 分页测试数据
def page_list(request):
    curPage = request.GET.get('page', 1)
    all_data = [{'name': f'alex{i}', 'age': i} for i in range(1, 307)]
    page_obj = Pagetions(curPage, len(all_data))

    return render(request, 'page_list.html',
                  {'all_data': all_data[page_obj.start:page_obj.end], 'page_html': page_obj.page_html()})
