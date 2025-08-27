import os
import io
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import re
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from .models import DocumentScan, ExtractedData, GeneratedCV, DocumentProcessingJob

logger = logging.getLogger(__name__)

class OCRService:
    """Service for optical character recognition and text extraction"""
    
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6'
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to PIL Image
        return Image.fromarray(thresh)
    
    def extract_text_from_image(self, image: Image.Image) -> Tuple[str, float]:
        """Extract text from a single image"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(processed_image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            return text.strip(), avg_confidence
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return "", 0.0
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, float, int]:
        """Extract text from PDF file"""
        try:
            all_text = ""
            total_confidence = 0
            page_count = 0
            
            # First try to extract text directly from PDF
            try:
                reader = PdfReader(pdf_path)
                page_count = len(reader.pages)
                
                for page in reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        all_text += text + "\n"
                
                if all_text.strip():
                    return all_text.strip(), 95.0, page_count  # High confidence for direct text extraction
            except:
                pass
            
            # If direct extraction fails, use OCR on images
            images = convert_from_path(pdf_path, dpi=300)
            page_count = len(images)
            
            for i, image in enumerate(images):
                text, confidence = self.extract_text_from_image(image)
                all_text += text + f"\n--- Page {i+1} ---\n"
                total_confidence += confidence
            
            avg_confidence = total_confidence / len(images) if images else 0
            
            return all_text.strip(), avg_confidence, page_count
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return "", 0.0, 0
    
    def extract_text_from_document(self, document_path: str) -> Tuple[str, float, int]:
        """Extract text from various document formats"""
        file_extension = os.path.splitext(document_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(document_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            image = Image.open(document_path)
            text, confidence = self.extract_text_from_image(image)
            return text, confidence, 1
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

class DataExtractionService:
    """Service for extracting structured data from text"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.date_pattern = re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b')
    
    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text"""
        contact_info = {}
        
        # Extract email
        emails = self.email_pattern.findall(text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        if phones:
            contact_info['phone'] = phones[0]
        
        return contact_info
    
    def extract_personal_info(self, text: str) -> Dict:
        """Extract personal information from text"""
        lines = text.split('\n')
        personal_info = {}
        
        # Try to extract name (usually in the first few lines)
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line) < 50:
                # Simple heuristic: if it looks like a name
                if not any(char.isdigit() for char in line) and '@' not in line:
                    personal_info['full_name'] = line
                    break
        
        # Extract dates (potential birth dates)
        dates = self.date_pattern.findall(text)
        if dates:
            personal_info['dates_found'] = dates
        
        return personal_info
    
    def extract_professional_info(self, text: str) -> Dict:
        """Extract professional information from text"""
        professional_info = {}
        
        # Common keywords for experience
        experience_keywords = ['experience', 'years', 'worked', 'employment', 'career']
        skills_keywords = ['skills', 'technologies', 'programming', 'software', 'tools']
        education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd']
        
        lines = text.lower().split('\n')
        
        # Extract skills section
        skills = []
        in_skills_section = False
        for line in lines:
            if any(keyword in line for keyword in skills_keywords):
                in_skills_section = True
                continue
            if in_skills_section and line.strip():
                if any(keyword in line for keyword in education_keywords + experience_keywords):
                    break
                skills.append(line.strip())
        
        if skills:
            professional_info['skills'] = ', '.join(skills[:10])  # Limit to first 10 skills
        
        # Extract education information
        education = []
        in_education_section = False
        for line in lines:
            if any(keyword in line for keyword in education_keywords):
                in_education_section = True
                education.append(line.strip())
                continue
            if in_education_section and line.strip():
                if any(keyword in line for keyword in skills_keywords + ['experience']):
                    break
                education.append(line.strip())
        
        if education:
            professional_info['education'] = '\n'.join(education[:5])  # Limit to first 5 lines
        
        return professional_info
    
    def extract_structured_data(self, text: str) -> Dict:
        """Extract all structured data from text"""
        extracted_data = {}
        
        # Extract different types of information
        contact_info = self.extract_contact_info(text)
        personal_info = self.extract_personal_info(text)
        professional_info = self.extract_professional_info(text)
        
        # Combine all extracted data
        extracted_data.update(contact_info)
        extracted_data.update(personal_info)
        extracted_data.update(professional_info)
        
        return extracted_data

class CVGenerationService:
    """Service for generating CVs and application forms"""
    
    def __init__(self):
        self.templates = {
            'modern': self._generate_modern_cv,
            'classic': self._generate_classic_cv,
            'professional': self._generate_professional_cv,
            'minimal': self._generate_minimal_cv,
            'creative': self._generate_creative_cv,
        }
    
    def generate_cv(self, extracted_data: ExtractedData, template_type: str = 'modern') -> bytes:
        """Generate CV PDF from extracted data"""
        if template_type not in self.templates:
            template_type = 'modern'
        
        return self.templates[template_type](extracted_data)
    
    def _generate_modern_cv(self, data: ExtractedData) -> bytes:
        """Generate modern style CV"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2C3E50'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#34495E'),
            borderWidth=1,
            borderColor=colors.HexColor('#BDC3C7'),
            borderPadding=5
        )
        
        # Build content
        story = []
        
        # Header
        if data.full_name:
            story.append(Paragraph(data.full_name, title_style))
        
        # Contact Information
        contact_info = []
        if data.email:
            contact_info.append(f"Email: {data.email}")
        if data.phone:
            contact_info.append(f"Phone: {data.phone}")
        if data.address:
            contact_info.append(f"Address: {data.address}")
        
        if contact_info:
            story.append(Paragraph(" | ".join(contact_info), styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Professional Summary
        if data.current_position or data.company:
            story.append(Paragraph("Professional Summary", heading_style))
            summary_text = f"{data.current_position or 'Professional'}"
            if data.company:
                summary_text += f" at {data.company}"
            if data.experience_years:
                summary_text += f" with {data.experience_years} years of experience"
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Skills
        if data.skills:
            story.append(Paragraph("Skills", heading_style))
            story.append(Paragraph(data.skills, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Education
        if data.education:
            story.append(Paragraph("Education", heading_style))
            story.append(Paragraph(data.education, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Certifications
        if data.certifications:
            story.append(Paragraph("Certifications", heading_style))
            story.append(Paragraph(data.certifications, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_classic_cv(self, data: ExtractedData) -> bytes:
        """Generate classic style CV"""
        # Similar structure but with classic styling
        return self._generate_modern_cv(data)  # Simplified for now
    
    def _generate_professional_cv(self, data: ExtractedData) -> bytes:
        """Generate professional style CV"""
        return self._generate_modern_cv(data)  # Simplified for now
    
    def _generate_minimal_cv(self, data: ExtractedData) -> bytes:
        """Generate minimal style CV"""
        return self._generate_modern_cv(data)  # Simplified for now
    
    def _generate_creative_cv(self, data: ExtractedData) -> bytes:
        """Generate creative style CV"""
        return self._generate_modern_cv(data)  # Simplified for now
    
    def generate_application_form(self, extracted_data: ExtractedData) -> bytes:
        """Generate application form PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph("Job Application Form", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Create form fields
        form_data = [
            ['Field', 'Information'],
            ['Full Name:', extracted_data.full_name or ''],
            ['Email:', extracted_data.email or ''],
            ['Phone:', extracted_data.phone or ''],
            ['Address:', extracted_data.address or ''],
            ['Current Position:', extracted_data.current_position or ''],
            ['Company:', extracted_data.company or ''],
            ['Years of Experience:', str(extracted_data.experience_years) if extracted_data.experience_years else ''],
        ]
        
        table = Table(form_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def merge_documents(self, cv_path: str, application_form_path: str, original_doc_path: str) -> bytes:
        """Merge CV, application form, and original document into single PDF"""
        writer = PdfWriter()
        
        # Add CV
        if os.path.exists(cv_path):
            cv_reader = PdfReader(cv_path)
            for page in cv_reader.pages:
                writer.add_page(page)
        
        # Add application form
        if os.path.exists(application_form_path):
            app_reader = PdfReader(application_form_path)
            for page in app_reader.pages:
                writer.add_page(page)
        
        # Add original document (if PDF)
        if os.path.exists(original_doc_path) and original_doc_path.endswith('.pdf'):
            orig_reader = PdfReader(original_doc_path)
            for page in orig_reader.pages:
                writer.add_page(page)
        
        # Write to buffer
        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        return buffer.getvalue()

class DocumentProcessingService:
    """Main service for coordinating document processing"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.extraction_service = DataExtractionService()
        self.cv_service = CVGenerationService()
    
    def process_document(self, document_scan: DocumentScan) -> bool:
        """Process a document scan through the complete pipeline"""
        try:
            # Update status
            document_scan.scan_status = 'processing'
            document_scan.save()
            
            start_time = time.time()
            
            # Extract text from document
            document_path = document_scan.original_document.path
            text, confidence, page_count = self.ocr_service.extract_text_from_document(document_path)
            
            # Update document scan with results
            document_scan.extracted_text = text
            document_scan.confidence_score = confidence
            document_scan.page_count = page_count
            document_scan.processing_time = time.time() - start_time
            document_scan.scan_status = 'completed'
            document_scan.save()
            
            # Extract structured data
            structured_data = self.extraction_service.extract_structured_data(text)
            
            # Create or update ExtractedData
            extracted_data, created = ExtractedData.objects.get_or_create(
                document_scan=document_scan,
                defaults=structured_data
            )
            
            if not created:
                # Update existing data
                for key, value in structured_data.items():
                    if hasattr(extracted_data, key) and value:
                        setattr(extracted_data, key, value)
                extracted_data.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {document_scan.id}: {str(e)}")
            document_scan.scan_status = 'failed'
            document_scan.error_message = str(e)
            document_scan.save()
            return False
    
    def generate_cv_and_forms(self, generated_cv: GeneratedCV) -> bool:
        """Generate CV and application form from extracted data"""
        try:
            generated_cv.generation_status = 'generating'
            generated_cv.save()
            
            # Get extracted data
            extracted_data = generated_cv.source_document.extracted_data
            
            # Generate CV
            cv_pdf = self.cv_service.generate_cv(extracted_data, generated_cv.template_type)
            cv_filename = f"cv_{generated_cv.id}.pdf"
            generated_cv.cv_file.save(cv_filename, ContentFile(cv_pdf))
            
            # Generate application form
            app_form_pdf = self.cv_service.generate_application_form(extracted_data)
            app_filename = f"application_{generated_cv.id}.pdf"
            generated_cv.application_form.save(app_filename, ContentFile(app_form_pdf))
            
            # Merge documents
            merged_pdf = self.cv_service.merge_documents(
                generated_cv.cv_file.path,
                generated_cv.application_form.path,
                generated_cv.source_document.original_document.path
            )
            merged_filename = f"merged_{generated_cv.id}.pdf"
            generated_cv.merged_document.save(merged_filename, ContentFile(merged_pdf))
            
            generated_cv.generation_status = 'completed'
            generated_cv.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating CV {generated_cv.id}: {str(e)}")
            generated_cv.generation_status = 'failed'
            generated_cv.error_message = str(e)
            generated_cv.save()
            return False
