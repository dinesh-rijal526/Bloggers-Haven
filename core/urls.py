# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('article/new/', views.create_article, name='create_article'),
    path('article/edit/<slug:slug>/', views.edit_article, name='edit_article'),
    path('article/delete/<slug:slug>/', views.delete_article, name='delete_article'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('comment/<slug:article_slug>/', views.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('like/<slug:article_slug>/', views.toggle_like, name='toggle_like'),
    path('category/', views.category, name='category'),
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
    path('about/', views.about_page, name='about'),
]