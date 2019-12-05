# -*-coding:utf-8-*-
# Author:Ds
from django.utils.safestring import mark_safe
from django.http.request import QueryDict

class Pagetions:

    def __init__(self, curPage, all_data, params=None, page_nums=10, max_show=9):
        '''
        :param curPage:   # 当前页数
        :param all_data:  # 数据总量
        :param page_nums:  # 每页多少条
        :param max_show:  # 显示总共几页
        '''


		### 保留分页的条件信息
        # 需要 拼接参数, 使用QueryDict 的urlencode方法,将参数 拼接, 并转码
        if not params:
            params=QueryDict(mutable=True) # 能够修改 QueryDict
        self.params=params
        # 1. 给self对象附上属性
        try:
            # 处理传递的当前页.  转换类型数值型
            curPage = int(curPage)
            if curPage < 0:
                curPage = 1
        except Exception:
            curPage = 1

        self.curPage = curPage  # 当前页
        self.all_data = all_data  # 总数据量

        # 2. 分页计算
        #  计算总页数
        total_num, more = divmod(all_data, page_nums)  # 总数据量  每页显示几条

        if more:  # 当数据不能显示完一页,多余几条, 必须个增加一页去进行显示
            total_num += 1

        # 3. 最大显示的页码数的一边,用于固定页码的数量
        half_show = max_show // 2

        # 4. 分页边界判断
        if total_num <= max_show:
            ### 总页数不超过 最大页码数
            page_start = 1  # 起始页
            page_end = total_num  # 终止页
        else:
            ### 总页数超过最大页码数
            ## 左极值
            if self.curPage - half_show <= 0:  # 当前页  小于 最大显示的页数
                page_start = 1  # 起始页
                page_end = max_show  # 终止页  一页显示的总页数

                ## 右极值
            elif self.curPage + half_show > total_num:  # 当前页的页数 大于 最大显示的页数
                page_start = total_num - max_show + 1  # +1  总页数-一屏幕显示几页+1
                page_end = total_num  # #  总页数

            else:
                ## 正常
                # 页码的起始位置
                page_start = self.curPage - half_show  # 起始位置 = 当前页 -最大显示的页码数
                # 页码的终止位置
                page_end = self.curPage + half_show  # 结束位置 = 当前页 +最大显示的页码数

        self.page_start = page_start
        self.page_end = page_end
        self.total_num = total_num

        ### 切片显示数据
        self.start = (self.curPage - 1) * page_nums
        self.end = self.curPage * page_nums


    def page_html(self):
        '''
        ## 此方法用于生成 前一页 和 后一页
        :return:
        '''
        # 存放生成的html字符串
        li_list = []

        if self.curPage == 1:
            # 第一页
            li_list.append(
                '<li class="disabled"><a aria-label="Previous"> <span aria-hidden="true">&laquo;</span></a></li>'
            )
        else:
            self.params['page']=self.curPage-1  #
            li_list.append(
                f'<li><a href="?{self.params.urlencode()}" aria-label="Previous"> <span aria-hidden="true">&laquo;</span></a></li>'
            )

        for el in range(self.page_start, self.page_end + 1):
            self.params['page']=el
            if el == self.curPage:
                li_list.append('<li class="active"><a href="?{}">{}</a></li>'.format(self.params.urlencode(), el))
            else:
                li_list.append('<li><a href="?{}">{}</a></li>'.format(self.params.urlencode(), el))

        if self.curPage <= self.total_num:
            # 右极值
            li_list.append(
                '<li class="disabled"><a aria-label="Previous"> <span aria-hidden="true">&raquo;</span></a></li>'
            )
        else:
            self.params['page']=self.curPage+1

            li_list.append(
                '<li><a href="?{}" aria-label="Previous"> <span aria-hidden="true">&raquo;</span></a></li>'.format(self.params.urlencode())
            )

        return mark_safe(''.join(li_list))
