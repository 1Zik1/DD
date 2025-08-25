from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio'
    
   
    def ready(self):
        # Импортируем сигналы для их регистрации
        import portfolio.signals