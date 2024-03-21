from django.apps import AppConfig

class OCPPAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ocpp_app'

    def ready(self):
        import ocpp_app.signals  # noqa
