from django.contrib import admin
from datastore.models import ServiceCategory, Service, ServiceUser, Data


def set_data(modeladmin, request, queryset):
    pass


set_data.short_description = "set data by service category"


class ServiceCategoryAdmin(admin.ModelAdmin):
    actions = [set_data]


admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service)
admin.site.register(ServiceUser)
admin.site.register(Data)
