from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid
import os

def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', str(instance.user.id), filename)

def cv_upload_path(instance, filename):
    """Generate upload path for generated CVs"""
    ext = filename.split('.')[-1]
    filename = f"cv_{uuid.uuid4()}.{ext}"
    return os.path.join('generated_cvs', str(instance.user.id), filename)

class DocumentScan(models.Model):
    """Model for storing scanned documents and extracted text"""
    DOCUMENT_TYPES = [
        ('resume', 'Resume/CV'),
        ('certificate', 'Certificate'),
        ('id_document', 'ID Document'),
        ('application', 'Application Form'),
        ('other', 'Other'),
    ]
    
    SCAN_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_scans')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    original_document = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'])]
    )
    extracted_text = models.TextField(blank=True, null=True)
    confidence_score = models.FloatField(default=0.0, help_text="OCR confidence score (0-100)")
    scan_status = models.CharField(max_length=20, choices=SCAN_STATUS, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Metadata
    file_size = models.PositiveIntegerField(default=0)
    page_count = models.PositiveIntegerField(default=1)
    processing_time = models.FloatField(default=0.0, help_text="Processing time in seconds")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document Scan"
        verbose_name_plural = "Document Scans"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()} ({self.scan_status})"

class ExtractedData(models.Model):
    """Model for storing structured data extracted from documents"""
    document_scan = models.OneToOneField(DocumentScan, on_delete=models.CASCADE, related_name='extracted_data')
    
    # Personal Information
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Professional Information
    current_position = models.CharField(max_length=200, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    education = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    
    # Additional structured data as JSON
    additional_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Extracted data for {self.document_scan}"

class GeneratedCV(models.Model):
    """Model for storing generated CVs and application forms"""
    CV_TEMPLATES = [
        ('modern', 'Modern Template'),
        ('classic', 'Classic Template'),
        ('creative', 'Creative Template'),
        ('minimal', 'Minimal Template'),
        ('professional', 'Professional Template'),
    ]
    
    GENERATION_STATUS = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_cvs')
    source_document = models.ForeignKey(DocumentScan, on_delete=models.CASCADE, related_name='generated_cvs')
    
    template_type = models.CharField(max_length=20, choices=CV_TEMPLATES, default='modern')
    cv_file = models.FileField(upload_to=cv_upload_path, blank=True, null=True)
    application_form = models.FileField(upload_to=cv_upload_path, blank=True, null=True)
    merged_document = models.FileField(upload_to=cv_upload_path, blank=True, null=True)
    
    generation_status = models.CharField(max_length=20, choices=GENERATION_STATUS, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Customization options
    custom_data = models.JSONField(default=dict, blank=True, help_text="Custom fields and modifications")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Generated CV"
        verbose_name_plural = "Generated CVs"
    
    def __str__(self):
        return f"CV for {self.user.username} - {self.get_template_type_display()}"

class DocumentProcessingJob(models.Model):
    """Model for tracking background processing jobs"""
    JOB_TYPES = [
        ('scan', 'Document Scanning'),
        ('extract', 'Data Extraction'),
        ('generate_cv', 'CV Generation'),
        ('merge_documents', 'Document Merging'),
    ]
    
    JOB_STATUS = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processing_jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='queued')
    
    # Related objects
    document_scan = models.ForeignKey(DocumentScan, on_delete=models.CASCADE, blank=True, null=True)
    generated_cv = models.ForeignKey(GeneratedCV, on_delete=models.CASCADE, blank=True, null=True)
    
    # Job details
    progress_percentage = models.PositiveIntegerField(default=0)
    result_data = models.JSONField(default=dict, blank=True)
    error_details = models.TextField(blank=True, null=True)
    
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Processing Job"
        verbose_name_plural = "Processing Jobs"
    
    def __str__(self):
        return f"{self.get_job_type_display()} - {self.status}"
