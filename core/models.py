from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    image = models.ImageField(upload_to='category/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Article(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField(Category)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = self.generate_unique_slug()
        
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        """Generate a unique slug even for empty titles"""
        base_slug = slugify(self.title) if self.title else 'untitled'
        if not base_slug:
            base_slug = 'article'
        
        unique_slug = base_slug
        suffix = 1
        
        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            suffix += 1
        
        return unique_slug

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, 
                              on_delete=models.CASCADE, 
                              related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user}"

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['article', 'user']]

    def __str__(self):
        return f"{self.user} likes {self.article}"

