from django.urls import path
from . import views
from users.views import profile_view  # добавлено

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('create/', views.create_post, name='create_post'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),  # добавлено
]
