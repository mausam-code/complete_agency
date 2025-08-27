"""
URL configuration for company_management project.
API-only configuration for React frontend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def api_root(request):
    """API root endpoint with basic information"""
    return JsonResponse({
        'message': 'Welcome to J.K. OVERSEAS PVT.LTD. Management API',
        'version': '1.0.0',
        'documentation': {
            'swagger': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'schema': request.build_absolute_uri('/api/schema/')
        },
        'endpoints': {
            'authentication': '/api/v1/accounts/auth/',
            'users': '/api/v1/accounts/users/',
            'projects': '/api/v1/core/projects/',
            'tasks': '/api/v1/core/tasks/',
            'attendance': '/api/v1/core/attendance/',
            'leave_requests': '/api/v1/core/leave-requests/',
            'expenses': '/api/v1/core/expenses/',
            'payroll': '/api/v1/core/payroll/',
            'notifications': '/api/v1/core/notifications/'
        }
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API root
    path('api/', api_root, name='api_root'),
    
    # API v1 endpoints
    path('api/v1/accounts/', include('accounts.api_urls')),
    path('api/v1/core/', include('core.api_urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Redirect root to API docs
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='home'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
