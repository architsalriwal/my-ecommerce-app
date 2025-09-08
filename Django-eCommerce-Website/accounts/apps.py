# C:\Users\archi\Downloads\Django-eCommerce-Website\Django-eCommerce-Website\accounts\apps.py


from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals
