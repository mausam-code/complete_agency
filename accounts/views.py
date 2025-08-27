# This file is kept for Django admin functionality only
# All user-facing views have been moved to api_views.py for React frontend

from django.shortcuts import render
from django.http import HttpResponse

def placeholder_view(request):
    """Placeholder view - all functionality moved to API"""
    return HttpResponse("This application now uses React frontend with API backend. Please access the API documentation at /api/docs/")
