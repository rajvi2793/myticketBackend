from django.apps import AppConfig


class TicketyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickety'

    def ready(self):
        import tickety.signals  # Ensure this matches the directory structure
