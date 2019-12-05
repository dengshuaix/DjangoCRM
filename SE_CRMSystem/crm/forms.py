# -*-coding:utf-8-*-
# Author:Ds
from crm import models
from django import forms  # 导入form 组件
from django.core.validators import ValidationError
from multiselectfield.forms.fields import MultiSelectFormField
from django.urls import reverse
import hashlib


class BSForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # print(name,field)
            if isinstance(field, (MultiSelectFormField, forms.BooleanField)):  # 判断form字段对象是不是属于多选框类型,属于则不添加class属性
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请填写{}'.format(field.__dict__['label'])


### 注册用户 form表单
class RegForm(forms.ModelForm):
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'autocomplete': 'off'}),
    )

    re_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入确认密码', 'autocomplete': 'off'}),
    )

    class Meta:
        model = models.UserProfile
        fields = '__all__'  # 全局的字段
        exclude = ['is_active']  # 不包含

        widgets = {
            'username': forms.EmailInput(attrs={'placeholder': '请输入用户名', 'autocomplete': 'off'}),
            'password': forms.PasswordInput(attrs={'placeholder': '请输入密码', 'autocomplete': 'off'}),
            'name': forms.TextInput(attrs={'placeholder': '请输入真实姓名', 'autocomplete': 'off'}),
            'mobile': forms.TextInput(attrs={'placeholder': '请输入手机号码', 'autocomplete': 'off'})
        }

    def clean(self):
        self._validate_unique = True  # 表示唯一性约束
        password = self.cleaned_data.get('password', '')
        re_password = self.cleaned_data.get('re_password')
        if password == re_password:  # 判断密码一致时
            md = hashlib.md5()
            md.update(password.encode('utf-8'))
            self.cleaned_data['password'] = md.hexdigest()  # 键值对cleaned_data中的password设置md5的密码值
            return self.cleaned_data  # 返回所有的键值对
        self.add_error('re_password', '两次密码不一致')  # 指定某个字段,给其在add_error方法添加错误信息
        raise ValidationError('两次密码不一致')  # 主动抛出异常,必须返回一个错误信息


### 添加客户 form
class CustomerForm(BSForm):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(request.path_info)
        print(reverse('crm:customer_add'))
        if request.path_info == reverse('crm:customer_add'):
            self.fields['consultant'].choices = [(request.user_obj.pk, request.user_obj), ]

    class Meta:
        model = models.Customer
        fields = '__all__'


### 添加跟进记录 form
class ConsultRecordForm(BSForm):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # OrderedDict
        # print(self.fields,type(self.fields))

        # print(list(self.fields['customer'].choices))

        ### 限制是当前用户的客户
        # 方式一  指定字段  values_list会变成元组形式
        # print(request.user_obj.customers.values_list('id','name'))
        # self.fields['customer'].choices=request.user_obj.customers.values_list('id','name')
        # 方式二  通过自定义的元组,
        self.fields['customer'].choices = [('', '---------')] + [(i.pk, str(i)) for i in
                                                                 request.user_obj.customers.all()]

        ### 限制跟进人 是当前的用户
        self.fields['consultant'].choices = [(request.user_obj.pk, request.user_obj)]

    class Meta:
        model = models.ConsultRecord
        fields = '__all__'


### 报名表
class EnrollmentFrom(BSForm):

    # def __init__(self, customer_id, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        super(EnrollmentFrom, self).__init__(*args, **kwargs)

        # customer_obj = models.Customer.objects.filter(pk=customer_id).first() if customer_id else self.instance.customer
        customer_obj = self.instance.customer


        self.fields['customer'].choices = [(customer_obj.pk, customer_obj)]
        self.fields['enrolment_class'].choices = [('', '---------')] + [(i.pk, str(i)) for i in
                                                                        customer_obj.class_list.all()]

        '''
        customer_obj = models.Customer.objects.filter(pk=customer_id).first()

        if customer_id:
            self.fields['customer'].choices = [(customer_id, customer_obj)]
            self.fields['enrolment_class'].choices =[('', '---------')] + [(i.pk, str(i)) for i in customer_obj.class_list.all()]
        else:
            self.fields['customer'].choices = [(self.instance.id, self.instance.customer), ]
            self.fields['enrolment_class'].choices = [('', '---------')] +[(i.pk, str(i)) for i in self.instance.customer.class_list.all()]
        '''

    class Meta:
        model = models.Enrollment
        fields = '__all__'


class ClassListFrom(BSForm):


    class Meta:
        model=models.ClassList
        fields='__all__'


class CourseRecordListFrom(BSForm):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        # 限制班级
        self.fields['re_class'].choices=[(self.instance.re_class_id,self.instance.re_class)]
        # 限制是当前用户
        self.fields['recorder'].choices=[(self.instance.recorder_id,self.instance.recorder)]
        # 限制讲师是当前班级的讲师
        self.fields['teacher'].choices=[(i.pk,str(i)) for i in self.instance.re_class.teachers.all()]

    class Meta:
        model=models.CourseRecord
        fields='__all__'


class StudyRecordListFrom(BSForm):


    class Meta:
        model=models.StudyRecord
        fields='__all__'