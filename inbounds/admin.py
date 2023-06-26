from django.contrib import admin
from . import models
from . import functions

# Register your models here.
class InboundUserInline(admin.TabularInline):
    model = models.InboundUser

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if not obj:
            formset.form.base_fields['uuid'].initial = functions.get_uuid

        return formset


class TlsInline(admin.StackedInline):
    model = models.Tls

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if not obj:
            formset.form.base_fields['server_name'].initial = 'discord.com'
            formset.form.base_fields['handshake_server'].initial = 'discord.com'
            formset.form.base_fields['private_key'].initial, formset.form.base_fields['public_key'].initial = functions.get_reality_keypair()
            formset.form.base_fields['short_id'].initial = functions.get_short_id()
        return formset


class TrafficUsageInline(admin.StackedInline):
    model = models.TrafficUsage


@admin.register(models.Inbound)
class InboundAdmin(admin.ModelAdmin):
    inlines = (InboundUserInline, TlsInline)


@admin.register(models.InboundUser)
class InboundUserAdmin(admin.ModelAdmin):
    inlines = (TrafficUsageInline, )
    list_display = ('uuid', 'connection_code')

    @admin.display(description="Connection Code")
    def connection_code(self, obj):
        return f"vless://{obj.uuid}@{obj.inbound.server.host}:{obj.inbound.listen_port}?encryption=none&flow=xtls-rprx-vision&security=reality&sni={obj.inbound.tls.server_name}&fp=chrome&pbk={obj.inbound.tls.public_key}&sid={obj.inbound.tls.short_id}&type=tcp&headerType=none#{obj.inbound.tag}"
