from django.contrib import admin
from django.db.models import Max
from .models import Charger, ChargerConfig, Connector, ChargingSession, IdTag, MeterValues
from unfold.admin import ModelAdmin

class ConnectorInline(admin.TabularInline):
    model = Connector
    fields = ('connector_id', 'status', 'type')
    readonly_fields = ('connector_id',)
    extra = 0  # Number of empty forms to display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('connector_id')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.connector_id:
                max_connector_id = Connector.objects.filter(charger=instance.charger).aggregate(Max('connector_id'))['connector_id__max']
                instance.connector_id = (max_connector_id or 0) + 1
            instance.save()
        formset.save_m2m()

@admin.register(Charger)
class ChargerAdmin(ModelAdmin):
    list_display = ('charger_id', 'vendor', 'model', 'enabled', 'price_per_kwh', 'verified', 'type', 'online')
    list_filter = ('enabled', 'verified', 'type')
    search_fields = ('charger_id', 'vendor', 'model')
    readonly_fields = ('online',)
    inlines = [ConnectorInline]

    def online(self, obj):
        return obj.online
    online.boolean = True

@admin.register(ChargerConfig)
class ChargerConfigAdmin(ModelAdmin):
    list_display = ('charger', 'key', 'value', 'readonly')
    list_filter = ('readonly',)
    search_fields = ('key',)

@admin.register(Connector)
class ConnectorAdmin(ModelAdmin):
    list_display = ('charger', 'connector_id', 'status', 'type')
    list_filter = ('status', 'type')
    search_fields = ('charger__charger_id', 'connector_id')

@admin.register(ChargingSession)
class ChargingSessionAdmin(ModelAdmin):
    list_display = ('connector', 'formatted_transaction_id', 'start_time', 'end_time', 'meter_start', 'meter_stop', 'limit', 'reason', 'limit_type')
    list_filter = ('reason', 'limit_type')
    search_fields = ('connector__charger__charger_id', 'transaction_id')

@admin.register(IdTag)
class IdTagAdmin(ModelAdmin):
    list_display = ('idtag', 'user', 'is_blocked', 'is_expired')
    list_filter = ('is_blocked',)
    search_fields = ('idtag', 'user__username')

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True

@admin.register(MeterValues)
class MeterValuesAdmin(ModelAdmin):
    list_display = ('id', 'value', 'unit', 'format', 'context', 'measurand', 'location', 'timestamp', 'charging_session', 'connector', 'charger')
    list_filter = ('unit', 'format', 'context', 'measurand', 'location')
    search_fields = ('id', 'value')
