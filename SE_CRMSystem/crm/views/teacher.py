# -*-coding:utf-8-*-
# Author:Ds

from django.shortcuts import render, HttpResponse, redirect, reverse
from .base import BaseView
from crm import models
from crm.forms import ClassListFrom, CourseRecordListFrom, StudyRecordListFrom
from utils.pagetions import Pagetions


class Class_list(BaseView):
    def get(self, request, *args, **kwargs):
        q = self.search(['campuses__name', 'start_date'])
        all_class = models.ClassList.objects.filter(q,teachers=request.user_obj)

        page_obj = Pagetions(request.GET.get('page'), all_class.count(), request.GET.copy(), 3, 3)

        return render(request, 'teacher/class_list.html',
                      {'all_class': all_class[page_obj.start:page_obj.end], 'page_html': page_obj.page_html()})


def class_change(request, pk=None):
    obj = models.ClassList.objects.filter(pk=pk).first()
    form_obj = ClassListFrom(instance=obj)

    if request.method == 'POST':
        form_obj = ClassListFrom(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            next = request.GET.get('next')
            if next:
                return redirect(next)

            return redirect('crm:class_list')

    title = '新增班级' if not pk else '编辑班级'
    return render(request, 'form.html', {'title': title, 'form_obj': form_obj})


class CourseRecordList(BaseView):
    def get(self, request, class_id, *args, **kwargs):

        all_courses_record = models.CourseRecord.objects.filter(re_class__id=class_id,teacher=request.user_obj)

        page_obj = Pagetions(request.GET.get('page'), all_courses_record.count(), request.GET.copy(), 3, 3)

        return render(request, 'teacher/course_record_list.html',
                      {'all_courses_record': all_courses_record[page_obj.start:page_obj.end],
                       'page_html': page_obj.page_html(), 'class_id': class_id})

    def multi_init(self):
        ## 批量创建学习记录
        # 课程记录的ID
        course_record_ids = self.request.POST.getlist('pk')

        # 查询出每一条课程记录对象
        course_records = models.CourseRecord.objects.filter(pk__in=course_record_ids)
        for course_record in course_records:
            # 通过班  去找客户, 通过学生的status状态判断 是学生还是客户.
            stutends = course_record.re_class.customer_set.all().filter(status='studying')
            #
            # for student in stutends:
            #     models.StudyRecord.objects.create(course_record=course_record,student=student)

            # 批量插入
            ### 多次重复插入 . 就会报错 ~~ ~~~ 已解决. 添加到列标签前,查一遍
            study_record_list = []
            for student in stutends:
                if not models.StudyRecord.objects.filter(course_record=course_record, student=student).exists():
                    study_record_list.append(models.StudyRecord(course_record=course_record, student=student))

            # bulk_create 需要一个列表 , batch_size 一次限制插入的条数
            # bulk_create 空列表,也不报错
            models.StudyRecord.objects.bulk_create(study_record_list, batch_size=10)


def course_record_change(request, pk=None, class_id=None):
    obj = models.CourseRecord(re_class_id=class_id,
                              recorder=request.user_obj) if class_id else models.CourseRecord.objects.filter(
        pk=pk).first()

    form_obj = CourseRecordListFrom(instance=obj)

    if request.method == 'POST':
        form_obj = CourseRecordListFrom(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            next = request.GET.get('next')
            if next:
                return redirect(next)
            # print(reverse('crm:course_record_list', args=(class_id,)))
            return redirect(reverse('crm:course_record_list', args=(class_id,)))

    title = '新增课程记录' if not pk else '编辑课程记录'
    return render(request, 'form.html', {'title': title, 'form_obj': form_obj})


from django.forms import modelformset_factory


def study_record_list(request, course_record_id):
    ModelFormSet = modelformset_factory(models.StudyRecord, StudyRecordListFrom, extra=0)
    #  queryset 查询的数据

    page_obj = Pagetions(request.GET.get('page'), len(models.StudyRecord.objects.filter(course_record_id=course_record_id)), request.GET.copy(), 2, 3)

    '''
    # 需要手动排序~~
    尝试自动排序将引发此错误。

    您需要将整个查询集传递给自动排序。
    '''

    form_set_obj = ModelFormSet(queryset=models.StudyRecord.objects.filter(course_record_id=course_record_id).order_by('id')[page_obj.start:page_obj.end])


    if request.method == 'POST':
        form_set_obj = ModelFormSet(queryset=models.StudyRecord.objects.filter(course_record_id=course_record_id).order_by('id')[page_obj.start:page_obj.end],data=request.POST)

        if form_set_obj.is_valid():
            form_set_obj.save()

            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('crm:study_record_list', course_record_id))

    # must_params=form_set_obj.management_form


    return render(request, 'teacher/study_record_list.html', {'form_set_obj':form_set_obj,'page_html':page_obj.page_html()})
