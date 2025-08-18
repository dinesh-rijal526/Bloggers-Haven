from django.db import models
from django.contrib.auth.models import User

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
        if not self.avatar:
            self.avatar = 'https://res.cloudinary.com/dhtgmo33l/image/upload/v1755492210/default_dfilos.png'
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username}'s Profile"