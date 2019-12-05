from django.conf import settings


def init_permission(user_obj, request):
    # 查询当前用户的权限信息
    permissions = user_obj.roles.exclude(permissions__url__isnull=True).values(
        'permissions__id',
        'permissions__parent_id',
        'permissions__parent__name',
        'permissions__url',
        'permissions__name',
        'permissions__title',
        'permissions__menu__title',
        'permissions__menu__icon',
        'permissions__menu__weight',
        'permissions__menu_id',
    ).distinct()

    # print(permissions)

    # 权限的列表
    permission_dict = {}
    # 菜单的字典
    menu_dict = {}

    for i in permissions:

        permission_dict[i['permissions__name']] = {'url': i['permissions__url'],
                                                   'id': i['permissions__id'],
                                                   'title': i['permissions__title'],
                                                   'pname': i['permissions__parent__name'],
                                                   'pid': i['permissions__parent_id']}

        menu_id = i.get('permissions__menu_id')
        if not menu_id:
            continue
        # 创建一级菜单的信息
        menu_dict.setdefault(menu_id, {
            'title': i['permissions__menu__title'],
            'icon': i['permissions__menu__icon'],
            'weight': i['permissions__menu__weight'],
            'children': [
            ]
        })
        # 添加二级菜单的信息
        menu_dict[menu_id]['children'].append(
            {'id': i['permissions__id'], 'title': i['permissions__title'], 'url': i['permissions__url']})

    # print(permission_dict)
    # 保存权限信息到session中
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict

    # 保存菜单的信息
    request.session[settings.MENU_SESSION_KEY] = menu_dict

    # 保存登陆状态
    request.session['is_login'] = True
    request.session['user_id'] = user_obj.pk
