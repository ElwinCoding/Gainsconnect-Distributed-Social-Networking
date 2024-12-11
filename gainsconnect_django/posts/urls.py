from django.urls import path
from . import views

urlpatterns = [
    path('post/<uuid:id>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/', views.post_list_creation, name='post-list-create'),
    path('stream/', views.StreamView.as_view(), name='stream'),
    path('posts/<uuid:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<uuid:post_id>/edit/', views.edit_post, name='edit_post'),
    path('repost/', views.RepostView.as_view(), name='repost'),
]