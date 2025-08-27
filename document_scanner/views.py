from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import json
import os
from datetime import datetime, timedelta

from accounts.decorators import role_required
from .models import DocumentScan, ExtractedData, GeneratedCV, DocumentProcessingJob
from .forms import DocumentUploadForm, CVGenerationForm, DocumentSearchForm
from .services import DocumentProcessingService
from .tasks import process_document_async, generate_cv_async

@login_required
def dashboard(request):
    """Document scanner dashboard"""
    # Get user's recent documents
    recent_scans = DocumentScan.objects.filter(user=request.user)[:5]
    recent_cvs = GeneratedCV.objects.filter(user=request.user)[:5]
    
    # Get statistics
    stats = {
        'total_documents': DocumentScan.objects.filter(user=request.user).count(),
        'completed_scans': DocumentScan.objects.filter(user=request.user, scan_status='completed').count(),
        'generated_cvs': GeneratedCV.objects.filter(user=request.user).count(),
        'processing_jobs': DocumentProcessingJob.objects.filter(
            user=request.user, 
            status__in=['queued', 'processing']
        ).count(),
    }
    
    context = {
        'recent_scans': recent_scans,
        'recent_cvs': recent_cvs,
        'stats': stats,
    }
    
    return render(request, 'document_scanner/dashboard.html', context)

@login_required
def upload_document(request):
    """Upload and process document"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document_scan = form.save(commit=False)
            document_scan.user = request.user
            document_scan.file_size = request.FILES['original_document'].size
            document_scan.save()
            
            # Start background processing
            process_document_async.delay(document_scan.id)
            
            messages.success(request, 'Document uploaded successfully! Processing will begin shortly.')
            return redirect('document_scanner:document_detail', pk=document_scan.id)
    else:
        form = DocumentUploadForm()
    
    return render(request, 'document_scanner/upload.html', {'form': form})

@login_required
def document_list(request):
    """List user's documents with search and filtering"""
    form = DocumentSearchForm(request.GET)
    documents = DocumentScan.objects.filter(user=request.user)
    
    # Apply filters
    if form.is_valid():
        if form.cleaned_data['document_type']:
            documents = documents.filter(document_type=form.cleaned_data['document_type'])
        
        if form.cleaned_data['status']:
            documents = documents.filter(scan_status=form.cleaned_data['status'])
        
        if form.cleaned_data['search_query']:
            query = form.cleaned_data['search_query']
            documents = documents.filter(
                Q(extracted_text__icontains=query) |
                Q(original_document__icontains=query)
            )
        
        if form.cleaned_data['date_from']:
            documents = documents.filter(created_at__gte=form.cleaned_data['date_from'])
        
        if form.cleaned_data['date_to']:
            documents = documents.filter(created_at__lte=form.cleaned_data['date_to'])
    
    # Pagination
    paginator = Paginator(documents.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'documents': page_obj,
    }
    
    return render(request, 'document_scanner/document_list.html', context)

@login_required
def document_detail(request, pk):
    """View document details and extracted data"""
    document = get_object_or_404(DocumentScan, pk=pk, user=request.user)
    
    try:
        extracted_data = document.extracted_data
    except ExtractedData.DoesNotExist:
        extracted_data = None
    
    generated_cvs = document.generated_cvs.all()
    processing_jobs = DocumentProcessingJob.objects.filter(document_scan=document)
    
    context = {
        'document': document,
        'extracted_data': extracted_data,
        'generated_cvs': generated_cvs,
        'processing_jobs': processing_jobs,
    }
    
    return render(request, 'document_scanner/document_detail.html', context)

@login_required
def generate_cv(request, document_pk):
    """Generate CV from extracted document data"""
    document = get_object_or_404(DocumentScan, pk=document_pk, user=request.user)
    
    if document.scan_status != 'completed':
        messages.error(request, 'Document must be processed before generating CV.')
        return redirect('document_scanner:document_detail', pk=document.pk)
    
    if request.method == 'POST':
        form = CVGenerationForm(request.POST)
        if form.is_valid():
            generated_cv = form.save(commit=False)
            generated_cv.user = request.user
            generated_cv.source_document = document
            generated_cv.save()
            
            # Start background CV generation
            generate_cv_async.delay(generated_cv.id)
            
            messages.success(request, 'CV generation started! You will be notified when complete.')
            return redirect('document_scanner:cv_detail', pk=generated_cv.id)
    else:
        form = CVGenerationForm()
    
    context = {
        'form': form,
        'document': document,
    }
    
    return render(request, 'document_scanner/generate_cv.html', context)

@login_required
def cv_list(request):
    """List user's generated CVs"""
    cvs = GeneratedCV.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(cvs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'cvs': page_obj,
    }
    
    return render(request, 'document_scanner/cv_list.html', context)

@login_required
def cv_detail(request, pk):
    """View CV details and download options"""
    cv = get_object_or_404(GeneratedCV, pk=pk, user=request.user)
    
    context = {
        'cv': cv,
    }
    
    return render(request, 'document_scanner/cv_detail.html', context)

@login_required
def download_file(request, file_type, pk):
    """Download generated files (CV, application form, merged document)"""
    cv = get_object_or_404(GeneratedCV, pk=pk, user=request.user)
    
    file_map = {
        'cv': cv.cv_file,
        'application': cv.application_form,
        'merged': cv.merged_document,
    }
    
    if file_type not in file_map:
        raise Http404("File type not found")
    
    file_field = file_map[file_type]
    if not file_field or not os.path.exists(file_field.path):
        raise Http404("File not found")
    
    with open(file_field.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_field.name)}"'
        return response

@login_required
def download_original(request, pk):
    """Download original document"""
    document = get_object_or_404(DocumentScan, pk=pk, user=request.user)
    
    if not document.original_document or not os.path.exists(document.original_document.path):
        raise Http404("File not found")
    
    with open(document.original_document.path, 'rb') as f:
        response = HttpResponse(f.read())
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.original_document.name)}"'
        return response

@login_required
@require_http_methods(["POST"])
def reprocess_document(request, pk):
    """Reprocess a document"""
    document = get_object_or_404(DocumentScan, pk=pk, user=request.user)
    
    # Reset status and start reprocessing
    document.scan_status = 'pending'
    document.extracted_text = ''
    document.confidence_score = 0.0
    document.error_message = ''
    document.save()
    
    # Start background processing
    process_document_async.delay(document.id)
    
    messages.success(request, 'Document reprocessing started!')
    return redirect('document_scanner:document_detail', pk=document.pk)

@login_required
@require_http_methods(["DELETE"])
def delete_document(request, pk):
    """Delete a document"""
    document = get_object_or_404(DocumentScan, pk=pk, user=request.user)
    document.delete()
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Document deleted successfully!')
    return redirect('document_scanner:document_list')

@login_required
@require_http_methods(["DELETE"])
def delete_cv(request, pk):
    """Delete a generated CV"""
    cv = get_object_or_404(GeneratedCV, pk=pk, user=request.user)
    cv.delete()
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'success': True})
    
    messages.success(request, 'CV deleted successfully!')
    return redirect('document_scanner:cv_list')

# API Views for real-time updates

@login_required
def api_processing_status(request, pk):
    """Get processing status for a document"""
    document = get_object_or_404(DocumentScan, pk=pk, user=request.user)
    
    # Get latest processing job
    latest_job = DocumentProcessingJob.objects.filter(
        document_scan=document
    ).order_by('-created_at').first()
    
    data = {
        'scan_status': document.scan_status,
        'confidence_score': document.confidence_score,
        'processing_time': document.processing_time,
        'error_message': document.error_message,
        'job_status': latest_job.status if latest_job else None,
        'progress_percentage': latest_job.progress_percentage if latest_job else 0,
    }
    
    return JsonResponse(data)

@login_required
def api_cv_status(request, pk):
    """Get CV generation status"""
    cv = get_object_or_404(GeneratedCV, pk=pk, user=request.user)
    
    # Get latest processing job
    latest_job = DocumentProcessingJob.objects.filter(
        generated_cv=cv
    ).order_by('-created_at').first()
    
    data = {
        'generation_status': cv.generation_status,
        'error_message': cv.error_message,
        'job_status': latest_job.status if latest_job else None,
        'progress_percentage': latest_job.progress_percentage if latest_job else 0,
        'files_ready': {
            'cv': bool(cv.cv_file),
            'application': bool(cv.application_form),
            'merged': bool(cv.merged_document),
        }
    }
    
    return JsonResponse(data)

@login_required
def api_dashboard_stats(request):
    """Get dashboard statistics"""
    stats = {
        'total_documents': DocumentScan.objects.filter(user=request.user).count(),
        'completed_scans': DocumentScan.objects.filter(
            user=request.user, 
            scan_status='completed'
        ).count(),
        'processing_scans': DocumentScan.objects.filter(
            user=request.user, 
            scan_status='processing'
        ).count(),
        'failed_scans': DocumentScan.objects.filter(
            user=request.user, 
            scan_status='failed'
        ).count(),
        'generated_cvs': GeneratedCV.objects.filter(user=request.user).count(),
        'active_jobs': DocumentProcessingJob.objects.filter(
            user=request.user,
            status__in=['queued', 'processing']
        ).count(),
    }
    
    return JsonResponse(stats)

# Admin views (for management users)

@role_required(['Super Admin', 'Admin'])
def admin_dashboard(request):
    """Admin dashboard for document scanner"""
    # Get system-wide statistics
    stats = {
        'total_documents': DocumentScan.objects.count(),
        'total_users': DocumentScan.objects.values('user').distinct().count(),
        'processing_jobs': DocumentProcessingJob.objects.filter(
            status__in=['queued', 'processing']
        ).count(),
        'failed_jobs': DocumentProcessingJob.objects.filter(status='failed').count(),
    }
    
    # Recent activity
    recent_documents = DocumentScan.objects.select_related('user').order_by('-created_at')[:10]
    recent_jobs = DocumentProcessingJob.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'recent_documents': recent_documents,
        'recent_jobs': recent_jobs,
    }
    
    return render(request, 'document_scanner/admin_dashboard.html', context)

@role_required(['Super Admin', 'Admin'])
def admin_document_list(request):
    """Admin view of all documents"""
    documents = DocumentScan.objects.select_related('user').order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    if status_filter:
        documents = documents.filter(scan_status=status_filter)
    
    user_filter = request.GET.get('user')
    if user_filter:
        documents = documents.filter(user__username__icontains=user_filter)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'documents': page_obj,
    }
    
    return render(request, 'document_scanner/admin_document_list.html', context)
