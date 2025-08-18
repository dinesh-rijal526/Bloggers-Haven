# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from .models import Article, Category, Comment, Like

def home(request):
    category_slug = request.GET.get('category')
    articles = Article.objects.filter(status=Article.PUBLISHED).order_by('-published_at')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(categories=category)
    
    categories = Category.objects.annotate(num_articles=Count('article'))
    
    context = {
        'articles': articles,
        'categories': categories,
        'selected_category': category_slug
    }
    return render(request, 'blog/article_list.html', context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.PUBLISHED)
    comments = article.comments.filter(parent=None).order_by('created_at')
    liked = article.likes.filter(user=request.user.id).exists() if request.user.is_authenticated else False
    
    context = {
        'article': article,
        'comments': comments,
        'liked': liked,
        'total_likes': article.likes.count()
    }
    return render(request, 'blog/article_detail.html', context)

@login_required
def create_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        status = request.POST.get('status')
        category_ids = request.POST.getlist('categories')
        cover_image = request.FILES.get('cover_image')
        
        article = Article(
            title=title,
            content=content,
            author=request.user,
            status=status,
            cover_image=cover_image
        )
        article.save()
        article.categories.set(category_ids)
        
        if article.status == "draft":
            messages.info(request, "Article saved as draft.")
            return redirect("profile")
        
        messages.success(request, 'Article created successfully!')
        return redirect('article_detail', slug=article.slug)
    
    categories = Category.objects.all()
    return render(request, 'blog/article_form.html', {
        'categories': categories,
        'status_choices': Article.STATUS_CHOICES
    })

@login_required
def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)
    
    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.status = request.POST.get('status')
        category_ids = request.POST.getlist('categories')
        
        if 'cover_image' in request.FILES:
            article.cover_image = request.FILES['cover_image']
        
        article.save()
        article.categories.set(category_ids)
        
        if article.status == "draft":
            messages.info(request, "Article saved as draft.")
            return redirect("profile")
        
        messages.success(request, 'Article updated successfully!')
        return redirect('article_detail', slug=article.slug)
    
    categories = Category.objects.all()
    return render(request, 'blog/article_form.html', {
        'article': article,
        'categories': categories,
        'status_choices': Article.STATUS_CHOICES
    })

@login_required
def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully!')
        return redirect('profile')
    
    return render(request, 'blog/article_confirm_delete.html', {'article': article})

@login_required
@require_POST
def add_comment(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    body = request.POST.get('body')
    parent_id = request.POST.get('parent_id')
    
    if body:
        comment = Comment(
            article=article,
            user=request.user,
            body=body
        )
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            comment.parent = parent_comment
        
        comment.save()
        messages.success(request, 'Comment added!')
    
    return redirect('article_detail', slug=article_slug)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    article_slug = comment.article.slug
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted!')
    
    return redirect('article_detail', slug=article_slug)

@login_required
@require_POST
def toggle_like(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    like, created = Like.objects.get_or_create(
        article=article,
        user=request.user
    )
    
    if not created:
        like.delete()
        messages.info(request, 'Removed like')
    else:
        messages.success(request, 'Liked article!')
    
    return redirect('article_detail', slug=article_slug)


def category(request):
    """Display all categories with search functionality"""
    search_query = request.GET.get('search', '')    
    categories = Category.objects.all()
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query)
        )
    
    categories = Category.objects.annotate(
        article_count=Count('article'),  
        author_count=Count('article__author', distinct=True),  
        published_count=Count('article', filter=Q(article__status='published')) 
    ).order_by('name')
    
    popular_categories = Category.objects.annotate(
        article_count=Count('article')
    ).filter(article_count__gt=0).order_by('-article_count')[:6]
    
    context = {
        'categories': categories,
        'popular_categories': popular_categories,
        'search_query': search_query,
    }
    
    return render(request, 'blog/category_list.html', context)

def category_articles(request, slug):
    """Display articles for a specific category"""
    category = get_object_or_404(Category, slug=slug)
    
    articles = Article.objects.filter(
        categories=category, 
        status=Article.PUBLISHED
    ).order_by('-published_at')
    
    context = {
        'category': category,
        'articles': articles,
        'articles_count': articles.count(),
    }
    
    return render(request, 'blog/category_article.html', context)

def about_page(request):
    return render(request, 'blog/about.html')