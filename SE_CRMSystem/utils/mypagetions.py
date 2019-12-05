# -*-coding:utf-8-*-
# Author:Ds
from django.http.request import QueryDict
from django.utils.safestring import mark_safe

class Paging:

    def __init__(self, curPage, all_data, params=None, page_items=10, max_show=7):

        if not params:
            params=QueryDict(mutable=True) # 能够修改 QueryDict

        self.params=params

        # 1. 当前页
        try:
            self.curPage = int(curPage)
            if curPage < 0:
                self.curPage = 1
        except Exception:
            self.curPage = 1

        # 2 . 分页
        '''
        page_total  总页数
        more  剩余条目数
        '''
        page_total, more = divmod(all_data, page_items)

        self.page_total = page_total

        if more:
            page_total += 1

        #
        half = max_show // 2

        # 3. 极值情况

        if page_total < max_show:
            # 总页数 小于
            self.page_start = 1
            self.page_end = page_total

        else:
            # 左右极值
            if self.curPage - half < 0:
                self.page_start = 1
                self.page_end = max_show
            elif curPage + half > page_total:
                self.page_end = page_total
                self.page_start = self.curPage - half + 1
            else:
                self.page_start = self.curPage - half
                self.page_end = self.curPage + half

        self.start = (self.curPage - 1) * page_items
        self.end = self.curPage * page_items

    def page_html(self):
        ' <li><a href="#" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'

        page_list = []

        if self.curPage==1:
            page_list.append(
                '<li class="disable"><a href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
            )
        else:
            self.params['page']=self.curPage-1
            page_list.append(
                f'<li><a href="?{self.params.urlencode()}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
            )

        for el in range(self.page_start,self.page_end+1):
            self.params['page']=el
            if el ==self.curPage:
                page_list.append(
                    f'<li class="active"><a href="?{self.params.urlencode()}" aria-label="Previous"><span aria-hidden="true">{el}</span></a></li>'
                )
            else:
                page_list.append(
                    f'<li><a href="?{self.params.urlencode()}" aria-label="Previous"><span aria-hidden="true">{el}</span></a></li>'
                )

        if self.curPage<=self.page_total:
            page_list.append(
                '<li class="disable"><a href="#" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'
            )
        else:
            self.params['page']=self.curPage+1
            page_list.append(
                f'<li><a href="?{self.params.urlencode()}" aria-label="Previous"><span aria-hidden="true"></span></a></li>'
            )

        return mark_safe(''.join(page_list))