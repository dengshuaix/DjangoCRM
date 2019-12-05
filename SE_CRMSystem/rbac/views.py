from django.shortcuts import render, redirect, HttpResponse
from rbac import models
from rbac.forms import RoleForm, MenuForm, PermissionForm, MultiPermissionForm
from django.db.models import Q
from crm.models import UserProfile


# Create your views here.
def role_list(request):
    all_roles = models.Role.objects.all()

    return render(request, 'rbac/role_list.html', {'all_roles': all_roles})


def role_change(request, pk=None, *args, **kwargs):
    obj = models.Role.objects.filter(pk=pk).first()
    form_obj = RoleForm(instance=obj)

    if request.method == 'POST':
        form_obj = RoleForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect('rbac:role_list')

    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def menu_list(request):
    mid = request.GET.get('mid')

    all_menus = models.Menu.objects.all()

    if not mid:
        all_permissions = models.Permission.objects.all()
    else:
        all_permissions = models.Permission.objects.filter(Q(menu_id=mid) | Q(parent__menu_id=mid))

    all_permissions = all_permissions.values('id', 'title', 'url', 'name', 'menu_id', 'menu__title', 'parent_id')
    permissions = {}

    for i in all_permissions:
        menu_id = i['menu_id']
        id = i['id']
        if menu_id:
            i['children'] = []
            permissions[id] = i

    print(permissions)
    for i in all_permissions:
        pid = i['parent_id']
        if pid:
            permissions[pid]['children'].append(i)

    return render(request, 'rbac/menu_list.html',
                  {'mid': mid, 'all_menus': all_menus, 'all_permissions': permissions.values()})


def menu_change(request, pk=None, *args, **kwargs):
    obj = models.Menu.objects.filter(pk=pk).first()
    form_obj = MenuForm(instance=obj)

    if request.method == 'POST':
        form_obj = MenuForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('rbac:menu_list')

    return render(request, 'meun_form.html', {'form_obj': form_obj})


def permission_change(request, pk=None, *args, **kwargs):
    obj = models.Permission.objects.filter(pk=pk).first()
    form_obj = PermissionForm(instance=obj)

    if request.method == 'POST':
        form_obj = PermissionForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('rbac:menu_list')

    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def delete(request, table, pk):
    model = getattr(models, table.capitalize())
    if not model:
        return HttpResponse('删除的表结构不存在')

    obj = model.objects.filter(pk=pk).first()

    if not obj:
        return HttpResponse('删除的数据不存在')
    obj.delete()

    return redirect(request.META.get('HTTP_REFERER'))


from django.forms import modelformset_factory, formset_factory

from rbac.service.routes import get_all_url_dict


def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')
    # 编辑  删除
    FormSet = modelformset_factory(models.Permission, MultiPermissionForm, extra=0)
    # 新增
    AddFormSet = formset_factory(MultiPermissionForm, extra=0)
    # 数据库所有的权限
    permissions = models.Permission.objects.all()
    # 路由系统的所有的url 权限
    router_dict = get_all_url_dict(ignore_namespace_list=['admin', ])

    # 数据库权限的name的集合
    permissions_name_set = set([i.name for i in permissions])
    # 路由系统中权限的name的集合
    router_name_set = set(router_dict.keys())

    add_name_set = router_name_set - permissions_name_set
    add_formset = AddFormSet(initial=[row for name, row in router_dict.items() if name in add_name_set])

    if request.method == 'POST' and post_type == 'add':
        add_formset = AddFormSet(request.POST)
        if add_formset.is_valid():
            permission_obj_list = [models.Permission(**i) for i in add_formset.cleaned_data]
            query_list = models.Permission.objects.bulk_create(permission_obj_list)
            add_formset = AddFormSet()
            for i in query_list:
                permissions_name_set.add(i.name)

    del_name_set = permissions_name_set - router_name_set
    del_formset = FormSet(queryset=models.Permission.objects.filter(name__in=del_name_set))

    update_name_set = permissions_name_set & router_name_set
    update_formset = FormSet(queryset=models.Permission.objects.filter(name__in=update_name_set))

    if request.method == 'POST' and post_type == 'update':
        update_formset = FormSet(request.POST)
        if update_formset.is_valid():
            update_formset.save()
            update_formset = FormSet(queryset=models.Permission.objects.filter(name__in=update_name_set))

    return render(
        request,
        'rbac/multi_permissions.html',
        {
            'del_formset': del_formset,
            'update_formset': update_formset,
            'add_formset': add_formset,
        }
    )


def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        user = UserProfile.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = models.Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    # 所有的用户
    user_list = UserProfile.objects.all()
    # 用户所拥有的角色 id
    user_has_roles = UserProfile.objects.filter(id=uid).values('id', 'roles')

    # 用户所拥有的角色id   {角色的id：None }
    user_has_roles_dict = {item['roles']: None for item in user_has_roles}
    # 所有的角色
    role_list = models.Role.objects.all()

    if rid:
        role_has_permissions = models.Role.objects.filter(id=rid, permissions__id__isnull=False).values('id',
                                                                                                        'permissions')
    elif uid and not rid:
        user = UserProfile.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.filter(permissions__id__isnull=False).values('id', 'permissions')
    else:
        role_has_permissions = []

    print(role_has_permissions)
    # 用户 或者 角色所拥有的权限
    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    all_menu_list = []

    """
    all_menu_list = [ 
            { id  title  children:[ 
                {id  title menu_id   'children':[
                    {  id  title parent_id  } 
                ] }
                
            ]  }  
            {'id': None, 'title': '其他', 'children': [
                  {  id  title parent_id  } 

            ]}
    ]
    
    """

    queryset = models.Menu.objects.values('id', 'title')  # [ { id  title } ]
    menu_dict = {}

    """
    menu_dict= { 一级菜单的id：{ id  title  children:[
         {id  title menu_id   'children':[
            {  id  title parent_id  } 
         
         ] }   
     ]  }
                none:{'id': None, 'title': '其他', 'children': [
                
                    {  id  title parent_id  } 
                ]}         
            }
    """

    for item in queryset:
        # { id  title  children:[]  }
        item['children'] = []
        menu_dict[item['id']] = item
        all_menu_list.append(item)

    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other

    root_permission = models.Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')
    root_permission_dict = {}

    """
     root_permission_dict = { 
        二级菜单的id : {id  title menu_id   'children':[
            {  id  title parent_id  } 
            
        ] }
        
     } 
    
    """

    for per in root_permission:
        # { id  title menu_id   'children':[] }
        per['children'] = []
        nid = per['id']
        menu_id = per['menu_id']
        root_permission_dict[nid] = per
        menu_dict[menu_id]['children'].append(per)

    node_permission = models.Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')

    for per in node_permission:
        # {  id  title parent_id  }
        pid = per['parent_id']
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per)

    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'user_list': user_list,  # 所有的用户
            'role_list': role_list,  # 所有的角色
            'user_has_roles_dict': user_has_roles_dict,  # 用户所拥有的角色
            'role_has_permissions_dict': role_has_permissions_dict,  # 角色拥有的权限
            'all_menu_list': all_menu_list,  # 菜单列表
            'uid': uid,
            'rid': rid
        }
    )
