from django.contrib import admin
from rbac import models


# Register your models here.

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'url', ]
    list_editable = ['title', 'url', ]


admin.site.register(models.Menu)
# admin.site.register(models.User)
admin.site.register(models.Role)
admin.site.register(models.Permission, PermissionAdmin)
