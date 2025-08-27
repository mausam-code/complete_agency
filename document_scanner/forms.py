from django import forms
from django.core.validators import FileExtensionValidator
from .models import DocumentScan, GeneratedCV, ExtractedData

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    
    class Meta:
        model = DocumentScan
        fields = ['document_type', 'original_document']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'original_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.tiff,.bmp',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_type'].empty_label = "Select document type"
        self.fields['original_document'].help_text = "Supported formats: PDF, JPG, PNG, TIFF, BMP (Max size: 10MB)"
    
    def clean_original_document(self):
        file = self.cleaned_data.get('original_document')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"File type '{file_extension}' is not supported.")
        
        return file

class CVGenerationForm(forms.ModelForm):
    """Form for generating CVs"""
    
    class Meta:
        model = GeneratedCV
        fields = ['template_type', 'custom_data']
        widgets = {
            'template_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'custom_data': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any additional information or customizations (JSON format)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template_type'].empty_label = "Select CV template"
        self.fields['custom_data'].required = False
        self.fields['custom_data'].help_text = "Optional: Additional data in JSON format"

class ExtractedDataForm(forms.ModelForm):
    """Form for editing extracted data"""
    
    class Meta:
        model = ExtractedData
        fields = [
            'full_name', 'email', 'phone', 'address', 'date_of_birth',
            'current_position', 'company', 'experience_years', 'skills',
            'education', 'certifications'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional for editing
        for field in self.fields.values():
            field.required = False

class DocumentSearchForm(forms.Form):
    """Form for searching and filtering documents"""
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in document text...'
        })
    )
    
    document_type = forms.ChoiceField(
        choices=[('', 'All Types')] + DocumentScan.DOCUMENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + DocumentScan.SCAN_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class CVCustomizationForm(forms.Form):
    """Form for customizing CV generation"""
    
    include_photo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    color_scheme = forms.ChoiceField(
        choices=[
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('red', 'Red'),
            ('purple', 'Purple'),
            ('orange', 'Orange'),
            ('gray', 'Gray'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    font_size = forms.ChoiceField(
        choices=[
            ('small', 'Small (10pt)'),
            ('medium', 'Medium (12pt)'),
            ('large', 'Large (14pt)'),
        ],
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    include_summary = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_skills = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_education = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_certifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    additional_sections = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional sections to include (one per line)'
        })
    )

class BulkDocumentForm(forms.Form):
    """Form for bulk document operations"""
    
    ACTION_CHOICES = [
        ('reprocess', 'Reprocess Documents'),
        ('delete', 'Delete Documents'),
        ('export', 'Export Data'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    document_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class DocumentFeedbackForm(forms.Form):
    """Form for providing feedback on document processing"""
    
    ACCURACY_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    accuracy_rating = forms.ChoiceField(
        choices=ACCURACY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    missing_data = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'What information was missed or incorrectly extracted?'
        })
    )
    
    suggestions = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any suggestions for improvement?'
        })
    )
    
    would_recommend = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
