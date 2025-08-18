from django.contrib import admin
from .models import *

class ArticleAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = slugify(obj.title)
            unique_slug = base_slug
            while Article.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            obj.slug = unique_slug
        super().save_model(request, obj, form, change)

admin.site.register(Article, ArticleAdmin)


admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Like)