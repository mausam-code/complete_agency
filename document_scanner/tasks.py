from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import logging
import time

from .models import DocumentScan, GeneratedCV, DocumentProcessingJob
from .services import DocumentProcessingService
from core.models import Notification

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_document_async(self, document_scan_id):
    """Asynchronously process a document scan"""
    try:
        # Get document scan
        document_scan = DocumentScan.objects.get(id=document_scan_id)
        
        # Create processing job
        job = DocumentProcessingJob.objects.create(
            user=document_scan.user,
            job_type='scan',
            document_scan=document_scan,
            status='processing',
            started_at=timezone.now()
        )
        
        # Update progress
        job.progress_percentage = 10
        job.save()
        
        # Initialize processing service
        processing_service = DocumentProcessingService()
        
        # Update progress
        job.progress_percentage = 30
        job.save()
        
        # Process the document
        success = processing_service.process_document(document_scan)
        
        if success:
            job.status = 'completed'
            job.progress_percentage = 100
            job.completed_at = timezone.now()
            job.result_data = {
                'confidence_score': document_scan.confidence_score,
                'page_count': document_scan.page_count,
                'processing_time': document_scan.processing_time
            }
            
            # Create notification
            Notification.objects.create(
                user=document_scan.user,
                title='Document Processing Complete',
                message=f'Your document "{document_scan.original_document.name}" has been processed successfully.',
                notification_type='success'
            )
            
            # Send email notification if enabled
            if hasattr(settings, 'SEND_EMAIL_NOTIFICATIONS') and settings.SEND_EMAIL_NOTIFICATIONS:
                send_processing_complete_email(document_scan.user, document_scan)
                
        else:
            job.status = 'failed'
            job.error_details = document_scan.error_message
            job.completed_at = timezone.now()
            
            # Create error notification
            Notification.objects.create(
                user=document_scan.user,
                title='Document Processing Failed',
                message=f'Failed to process document "{document_scan.original_document.name}". Please try again.',
                notification_type='error'
            )
        
        job.save()
        return success
        
    except DocumentScan.DoesNotExist:
        logger.error(f"Document scan {document_scan_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error processing document {document_scan_id}: {str(e)}")
        
        # Update job status
        try:
            job.status = 'failed'
            job.error_details = str(e)
            job.completed_at = timezone.now()
            job.save()
        except:
            pass
        
        return False

@shared_task(bind=True)
def generate_cv_async(self, generated_cv_id):
    """Asynchronously generate CV and application form"""
    try:
        # Get generated CV object
        generated_cv = GeneratedCV.objects.get(id=generated_cv_id)
        
        # Create processing job
        job = DocumentProcessingJob.objects.create(
            user=generated_cv.user,
            job_type='generate_cv',
            generated_cv=generated_cv,
            status='processing',
            started_at=timezone.now()
        )
        
        # Update progress
        job.progress_percentage = 20
        job.save()
        
        # Initialize processing service
        processing_service = DocumentProcessingService()
        
        # Update progress
        job.progress_percentage = 50
        job.save()
        
        # Generate CV and forms
        success = processing_service.generate_cv_and_forms(generated_cv)
        
        if success:
            job.status = 'completed'
            job.progress_percentage = 100
            job.completed_at = timezone.now()
            job.result_data = {
                'cv_generated': bool(generated_cv.cv_file),
                'application_generated': bool(generated_cv.application_form),
                'merged_generated': bool(generated_cv.merged_document),
                'template_type': generated_cv.template_type
            }
            
            # Create notification
            Notification.objects.create(
                user=generated_cv.user,
                title='CV Generation Complete',
                message=f'Your CV has been generated successfully using the {generated_cv.get_template_type_display()} template.',
                notification_type='success'
            )
            
            # Send email notification if enabled
            if hasattr(settings, 'SEND_EMAIL_NOTIFICATIONS') and settings.SEND_EMAIL_NOTIFICATIONS:
                send_cv_complete_email(generated_cv.user, generated_cv)
                
        else:
            job.status = 'failed'
            job.error_details = generated_cv.error_message
            job.completed_at = timezone.now()
            
            # Create error notification
            Notification.objects.create(
                user=generated_cv.user,
                title='CV Generation Failed',
                message='Failed to generate your CV. Please try again or contact support.',
                notification_type='error'
            )
        
        job.save()
        return success
        
    except GeneratedCV.DoesNotExist:
        logger.error(f"Generated CV {generated_cv_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error generating CV {generated_cv_id}: {str(e)}")
        
        # Update job status
        try:
            job.status = 'failed'
            job.error_details = str(e)
            job.completed_at = timezone.now()
            job.save()
        except:
            pass
        
        return False

@shared_task
def cleanup_old_documents():
    """Clean up old documents and files"""
    try:
        # Delete documents older than 90 days (configurable)
        cutoff_date = timezone.now() - timezone.timedelta(days=90)
        
        old_documents = DocumentScan.objects.filter(created_at__lt=cutoff_date)
        deleted_count = 0
        
        for document in old_documents:
            try:
                # Delete associated files
                if document.original_document:
                    document.original_document.delete()
                
                # Delete generated CVs and their files
                for cv in document.generated_cvs.all():
                    if cv.cv_file:
                        cv.cv_file.delete()
                    if cv.application_form:
                        cv.application_form.delete()
                    if cv.merged_document:
                        cv.merged_document.delete()
                    cv.delete()
                
                document.delete()
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Error deleting document {document.id}: {str(e)}")
        
        logger.info(f"Cleaned up {deleted_count} old documents")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return 0

@shared_task
def cleanup_failed_jobs():
    """Clean up old failed processing jobs"""
    try:
        # Delete failed jobs older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        
        old_jobs = DocumentProcessingJob.objects.filter(
            status='failed',
            created_at__lt=cutoff_date
        )
        
        deleted_count = old_jobs.count()
        old_jobs.delete()
        
        logger.info(f"Cleaned up {deleted_count} old failed jobs")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up failed jobs: {str(e)}")
        return 0

@shared_task
def generate_processing_report():
    """Generate daily processing report for admins"""
    try:
        from datetime import datetime, timedelta
        
        # Get yesterday's data
        yesterday = timezone.now() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Calculate statistics
        total_documents = DocumentScan.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        successful_scans = DocumentScan.objects.filter(
            created_at__range=[start_date, end_date],
            scan_status='completed'
        ).count()
        
        failed_scans = DocumentScan.objects.filter(
            created_at__range=[start_date, end_date],
            scan_status='failed'
        ).count()
        
        generated_cvs = GeneratedCV.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        successful_cvs = GeneratedCV.objects.filter(
            created_at__range=[start_date, end_date],
            generation_status='completed'
        ).count()
        
        # Calculate average processing time
        avg_processing_time = DocumentScan.objects.filter(
            created_at__range=[start_date, end_date],
            scan_status='completed'
        ).aggregate(avg_time=models.Avg('processing_time'))['avg_time'] or 0
        
        # Create report data
        report_data = {
            'date': yesterday.strftime('%Y-%m-%d'),
            'total_documents': total_documents,
            'successful_scans': successful_scans,
            'failed_scans': failed_scans,
            'success_rate': (successful_scans / total_documents * 100) if total_documents > 0 else 0,
            'generated_cvs': generated_cvs,
            'successful_cvs': successful_cvs,
            'cv_success_rate': (successful_cvs / generated_cvs * 100) if generated_cvs > 0 else 0,
            'avg_processing_time': round(avg_processing_time, 2)
        }
        
        # Send report to admins
        admin_users = User.objects.filter(
            userprofile__role__in=['Super Admin', 'Admin']
        )
        
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title='Daily Processing Report',
                message=f"Documents processed: {total_documents} (Success: {successful_scans}, Failed: {failed_scans}). CVs generated: {generated_cvs}.",
                notification_type='info'
            )
        
        logger.info(f"Generated processing report for {yesterday.strftime('%Y-%m-%d')}")
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating processing report: {str(e)}")
        return None

@shared_task
def batch_reprocess_documents(document_ids, user_id):
    """Batch reprocess multiple documents"""
    try:
        user = User.objects.get(id=user_id)
        documents = DocumentScan.objects.filter(id__in=document_ids, user=user)
        
        processed_count = 0
        failed_count = 0
        
        for document in documents:
            try:
                # Reset document status
                document.scan_status = 'pending'
                document.extracted_text = ''
                document.confidence_score = 0.0
                document.error_message = ''
                document.save()
                
                # Process document
                processing_service = DocumentProcessingService()
                success = processing_service.process_document(document)
                
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error reprocessing document {document.id}: {str(e)}")
                failed_count += 1
        
        # Create notification
        Notification.objects.create(
            user=user,
            title='Batch Reprocessing Complete',
            message=f'Reprocessed {processed_count} documents successfully. {failed_count} failed.',
            notification_type='info' if failed_count == 0 else 'warning'
        )
        
        return {'processed': processed_count, 'failed': failed_count}
        
    except Exception as e:
        logger.error(f"Error in batch reprocessing: {str(e)}")
        return {'processed': 0, 'failed': len(document_ids)}

def send_processing_complete_email(user, document_scan):
    """Send email notification when document processing is complete"""
    try:
        subject = 'Document Processing Complete'
        message = f"""
        Hello {user.get_full_name() or user.username},
        
        Your document "{document_scan.original_document.name}" has been processed successfully.
        
        Processing Details:
        - Confidence Score: {document_scan.confidence_score:.1f}%
        - Processing Time: {document_scan.processing_time:.2f} seconds
        - Pages Processed: {document_scan.page_count}
        
        You can now view the extracted data and generate CVs from this document.
        
        Best regards,
        Company Management System
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
        )
        
    except Exception as e:
        logger.error(f"Error sending processing complete email: {str(e)}")

def send_cv_complete_email(user, generated_cv):
    """Send email notification when CV generation is complete"""
    try:
        subject = 'CV Generation Complete'
        message = f"""
        Hello {user.get_full_name() or user.username},
        
        Your CV has been generated successfully using the {generated_cv.get_template_type_display()} template.
        
        Generated Files:
        - CV Document: {'✓' if generated_cv.cv_file else '✗'}
        - Application Form: {'✓' if generated_cv.application_form else '✗'}
        - Merged Document: {'✓' if generated_cv.merged_document else '✗'}
        
        You can download your files from the CV details page.
        
        Best regards,
        Company Management System
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
        )
        
    except Exception as e:
        logger.error(f"Error sending CV complete email: {str(e)}")
