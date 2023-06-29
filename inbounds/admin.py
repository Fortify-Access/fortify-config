from django.contrib import admin
from . import models

# Register your models here.
class InboundUserInline(admin.TabularInline):
    model = models.InboundUser


class TlsInline(admin.StackedInline):
    model = models.Tls


class TransportInline(admin.StackedInline):
    model = models.Transport


@admin.register(models.Inbound)
class InboundAdmin(admin.ModelAdmin):
    inlines = (InboundUserInline, TlsInline, TransportInline)


@admin.register(models.InboundUser)
class InboundUserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'connection_code')

    @admin.display(description="Connection Code")
    def connection_code(self, obj):
        return f"vless://{obj.uuid}@{obj.inbound.server.host}:{obj.inbound.listen_port}?encryption=none&flow=xtls-rprx-vision&security=reality&sni={obj.inbound.tls.server_name}&fp=chrome&pbk={obj.inbound.tls.public_key}&sid={obj.inbound.tls.short_id}&type=tcp&headerType=none#{obj.inbound.tag}"
