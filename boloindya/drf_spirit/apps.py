from django.apps import AppConfig


class DrfSpiritConfig(AppConfig):
    name = 'drf_spirit'
    verbose_name = "DRF Spirit"

    def ready(self):
        from .signals import post_comment_save, post_comment_delete
