from django.contrib import admin
from . import models as config_models
from inbounds import models as inbound_models

# Register your models here.
class InboundInline(admin.TabularInline):
    model = inbound_models.Inbound
    extra = 0


@admin.register(config_models.Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('host', 'location')
    inlines = (InboundInline, )
    readonly_fields = ('is_local_server',)


@admin.register(config_models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
