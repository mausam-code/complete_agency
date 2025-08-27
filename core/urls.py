# Legacy URLs - functionality moved to API
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Placeholder - all functionality moved to API
    path('', views.placeholder_view, name='placeholder'),
]
