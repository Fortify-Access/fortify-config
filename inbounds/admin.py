from django.contrib import admin
from . import models
from . import functions

# Register your models here.
class InboundUserInline(admin.TabularInline):
    model = models.InboundUser

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(InboundUserInline, self).get_formset(request, obj, **kwargs)
        if not obj:
            formset.form.base_fields['uuid'].initial = functions.get_uuid()
        return formset


class TlsInline(admin.StackedInline):
    model = models.Tls

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(TlsInline, self).get_formset(request, obj, **kwargs)
        if not obj:
            formset.form.base_fields['private_key'].initial, formset.form.base_fields['public_key'].initial = functions.get_reality_keypair()
            formset.form.base_fields['short_id'].initial = functions.get_short_id()
        return formset


class TransportInline(admin.StackedInline):
    model = models.Transport


@admin.register(models.Inbound)
class InboundAdmin(admin.ModelAdmin):
    inlines = (InboundUserInline, TlsInline, TransportInline)


@admin.register(models.InboundUser)
class InboundUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid')
    readonly_fields = ('name', )
