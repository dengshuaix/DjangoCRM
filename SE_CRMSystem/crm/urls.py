"""SE_CRMSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from crm.views import auth,consultant,teacher
urlpatterns = [
    url(r'^login/', auth.login , name='login'),
    url(r'^index/', auth.index , name='index'),
    url(r'^register/', auth.register ,name='register'),
    # url(r'^customer_list/', views.Customers.as_view() ,name='customer_list'),



    #### 客户表
    url(r'^customer_list/', consultant.Customer_list.as_view(),name='customer_list'),  # 公户 展示客户列表
    url(r'^my_customer_list/', consultant.Customer_list.as_view(),name='my_customer_list'),  # 私户 展示客户列表

    url(r'^customer_add_ajax/', consultant.customer_add_ajax,name='customer_add_ajax'),  # ajax添加客户
    # url(r'^customer_add/', views.customer_add,name='customer_add'),  # 添加客户
    # url(r'^customer_edit/(\d+)', views.customer_edit,name='customer_edit'),  # 编辑客户

    ##### 统一函数, 添加和保存都可使用同一个是视图函数
    url(r'^customer_add/', consultant.customer_change, name='customer_add'),
    url(r'^customer_edit/(\d+)/', consultant.customer_change, name='customer_edit'),


    ### 模糊搜索
    url(r'^customer_filed_search/', consultant.Customer_list.as_view(), name='customer_filed_search'),

    ### 删除 (更改状态)
    # url(r'^(\w+)_del/(\d+)/', views.delete, name='delete'),

    url(r'^page_list/', consultant.page_list,name='page_list'),  # 分页测试




    ##### 跟进记录表
    url(r'^consultrecord_list/$', consultant.ConsultRecord_list.as_view(), name='consultrecord_list'),
    url(r'^one_customer_record_list/(?P<customer_id>\d+)/', consultant.ConsultRecord_list.as_view(), name='one_customer_record_list'),
    # 编辑和添加跟进记录
    url(r'^consultrecord_add/', consultant.consultrecord_change, name='consultrecord_add'),
    url(r'^consultrecord_edit/(\d+)/', consultant.consultrecord_change, name='consultrecord_edit'),


    #### 报名表
    # 展示所有的报名记录
    url(r'^enrollment_list/$', consultant.Enrollment_list.as_view(), name='enrollment_list'),
    # 展示一条用户的报名记录
    url(r'^one_enrollment_list/(?P<customer_id>\d+)/$', consultant.Enrollment_list.as_view(), name='one_enrollment_list'),
    # 添加报名
    url(r'^enrollment_add/(?P<customer_id>\d+)/$', consultant.enrollment_change, name='enrollment_add'),
    # 编辑报名
    url(r'^enrollment_edit/(?P<pk>\d+)/', consultant.enrollment_change, name='enrollment_edit'),


    ### 班级表 展示列表
    url(r'^class_list/$', teacher.Class_list.as_view(), name='class_list'),
    # 添加班级
    url(r'^class_add/$', teacher.class_change, name='class_add'),
    # 编辑班级
    url(r'^class_edit/(?P<pk>\d+)$', teacher.class_change, name='class_edit'),


    ### 课程记录表
    url(r'^course_record_list/(?P<class_id>\d+)$', teacher.CourseRecordList.as_view(), name='course_record_list'),
    # 添加课程记录
    url(r'^course_record_add/(?P<class_id>\d+)$', teacher.course_record_change, name='course_record_add'),
    # 编辑课程记录
    url(r'^course_record_edit/(?P<pk>\d+)/$', teacher.course_record_change, name='course_record_edit'),


    ### 展示学习记录
    url(r'^study_record_list/(?P<course_record_id>\d+)$', teacher.study_record_list, name='study_record_list'),

]
