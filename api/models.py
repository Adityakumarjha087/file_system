from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('ops', 'Operations'),
        ('client', 'Client'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Default role is 'client' if not specified
        Profile.objects.create(user=instance, role='client')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class UploadedFile(models.Model):
    ALLOWED_EXTENSIONS = ['.docx', '.pptx', '.xlsx']
    
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)
    
    def __str__(self):
        return self.original_filename
    
    def get_file_extension(self):
        import os
        return os.path.splitext(self.original_filename)[1].lower()
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.original_filename = self.file.name
            if self.get_file_extension() not in self.ALLOWED_EXTENSIONS:
                raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}")
        super().save(*args, **kwargs)
