from django import template
from django.conf import settings
from collections import OrderedDict

register = template.Library()


@register.inclusion_tag('rbac/menu.html')
def menu(request):
    # url = request.path_info
    menu_dict = request.session.get(settings.MENU_SESSION_KEY)
    ret = sorted(menu_dict, key=lambda x: menu_dict[x]['weight'], reverse=True)
    od = OrderedDict()

    for i in ret:
        item = od[i] = menu_dict[i]
        item['class'] = 'hidden'
        for p in item['children']:

            if p['id'] == request.current_menu_id:
                item.pop('class')
                p['class'] = 'active'
                break

    return {'menu_list': od.values(),}


@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    return {'breadcrumb_list': request.breadcrumb_list}


@register.filter
def has_permission(request, name):
    if name in request.session.get(settings.PERMISSION_SESSION_KEY):
        return True

@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params['rid'] = rid
    return params.urlencode()
