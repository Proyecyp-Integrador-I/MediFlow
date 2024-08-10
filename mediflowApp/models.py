from django.db import models

class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/')
    result_analysis = models.TextField(blank=True)
    is_analyzed = models.BooleanField(default=False)

    def __str__(self):
        return f"File {self.id} - {self.date}"