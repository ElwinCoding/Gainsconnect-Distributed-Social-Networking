from django.urls import path
from .views import add_comment_api, add_like_api, get_comments_api, get_like_count_api

urlpatterns = [
    path('<uuid:post_uid>/comments/', get_comments_api, name='get_comments_api'),
    path('<uuid:post_uid>/comments/add/', add_comment_api, name='add_comment_api'),
    path('<uuid:post_uid>/likes/count/', get_like_count_api, name='get_like_count_api'),
    path('<uuid:post_uid>/likes/add/', add_like_api, name='add_like_api'),


#this is wrong, needs to go into api urls, and 

    # Fully implemented endpoints (local and remote)
    
]

