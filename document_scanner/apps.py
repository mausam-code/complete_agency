from django.apps import AppConfig

class DocumentScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'document_scanner'
    verbose_name = 'Document Scanner'
    
    def ready(self):
        import document_scanner.signals
