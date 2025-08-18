from django.db import models
from django.contrib.auth.models import User

def get_default_avatar_path():
    return 'https://res.cloudinary.com/dhtgmo33l/image/upload/v1755492210/default_dfilos.png'  

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )
    dark_mode = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = get_default_avatar_path()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"