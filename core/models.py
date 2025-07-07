from django.db import models
from django.contrib.auth.models import User

class ScanResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='scans/')
    result = models.CharField(max_length=20,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    def save(self, *args, **kwargs):
        if not self.name and self.image:
            self.name = self.image.name.split('/')[-1]
        super().save(*args, **kwargs)





# Create your models here.
