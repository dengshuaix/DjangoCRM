from django.db import models

class Menu(models.Model):
    """
    一级菜单
    """
    title = models.CharField(max_length=32, verbose_name='一级菜单标题')
    icon = models.CharField(max_length=64, verbose_name='图标', blank=True, null=True)
    weight = models.IntegerField(default=1, verbose_name='权重')

    def __str__(self):
        return self.title


class Permission(models.Model):
    """
    menu_id  有menu_id  当前的权限是一个二级菜单
             没有menu_id   当前的权限时一个普通的权限

    """

    url = models.CharField(verbose_name='权限', max_length=108)
    name = models.CharField(verbose_name='url的别名', max_length=32, unique=True)
    title = models.CharField(verbose_name='标题', max_length=32)
    menu = models.ForeignKey(Menu, verbose_name='一级菜单', blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name='父权限', blank=True, null=True)

    def __str__(self):
        return self.title


class Role(models.Model):
    name = models.CharField('角色名称', max_length=32)
    permissions = models.ManyToManyField('Permission', verbose_name='角色所拥有的权限', blank=True)

    def __str__(self):
        return self.name


class User(models.Model):
    # username = models.CharField('用户名', max_length=32)
    # password = models.CharField('密码', max_length=32)
    roles = models.ManyToManyField(Role, verbose_name='用户所拥有的角色', blank=True)

    def __str__(self):
        return self.username

    class Meta:
        abstract = True # 基类 不会在数据库中生成表  让别的表继承
