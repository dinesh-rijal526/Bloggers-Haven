from django import forms
from .models import Article, Comment

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'categories', 'cover_image', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 15, 'class': 'markdown-editor'}),
            'status': forms.RadioSelect(choices=[
                ('draft', 'Save as Draft'),
                ('published', 'Publish Immediately')
            ])
        }
        help_texts = {
            'categories': 'Hold Ctrl/Cmd to select multiple categories'
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Join the discussion...',
                'class': 'comment-textarea'
            })
        }