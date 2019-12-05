# -*-coding:utf-8-*-
# Author:Ds
from django import template
from django.urls import reverse
from django.http.request import QueryDict
register=template.Library()

@register.simple_tag
def url_revers(request,name,*args,**kwargs):

    url=reverse(name,args=args,kwargs=kwargs) # 生成URL连接
    # print(url)
    next=request.get_full_path()  #获得全路径
    # print(next)
    qd=QueryDict(mutable=True)   #
    qd['next']=next
    # print(qd)
    # print(qd.__dict__)
    print(qd.urlencode()) # next=%2Fcrm%2Fone_enrollment_list%2F1%2F%3Fnext%3D%252Fcrm%252Fmy_customer_list%252F
    return '{}?{}'.format(url,qd.urlencode())