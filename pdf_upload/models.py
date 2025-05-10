from django.db import models
import os
from django.core.files.storage import FileSystemStorage
import os

custom_storage = FileSystemStorage(
    location=os.path.join('C:\\', 'temp_unlock_pdf'),
    base_url='/media/'
)

class PDFFile(models.Model):
    file = models.FileField(upload_to='locked_pdfs/', storage=custom_storage)
    unlocked_file = models.FileField(upload_to='unlocked_pdfs/', storage=custom_storage, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_success = models.BooleanField(default=False)
    password = models.CharField(max_length=10, null=True, blank=True)
    attempts = models.IntegerField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return os.path.basename(self.file.name)

    def filename(self):
        return os.path.basename(self.file.name)