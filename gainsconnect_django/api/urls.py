from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, re_path
from posts.views import *
from follow.views import *
from authors.views import *
from comments.views import *

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('authors/<uuid:author_uid>/posts/<uuid:post_uid>/', PostDetailView.as_view(), name='post-detail'),
    path('authors/<uuid:author_uid>/posts/<uuid:post_uid>', PostDetailView.as_view(), name='post-detail'),
    path('posts/', post_list_creation, name='post-list-create'),
    path('stream/', StreamView.as_view(), name='stream'),
    path('posts/<uuid:post_uid>/delete/', delete_post, name='delete_post'),
    path('posts/<uuid:post_uid>/edit/', edit_post, name='edit_post'),
    path('repost/', RepostView.as_view(), name='repost'),
    path('authors/', AuthorView.as_view(), name='getAuthors'),
    path('authors/<str:uid>/followers', GetFollowersView.as_view(),name='followers'),
    path('authors/<str:uid>/followers/<path:fid>', HandleRequestView.as_view(), name='handleRequest'),
    path('authors/<str:uid>/posts/', ProfilePostsView.as_view(), name='local-profile-posts'),
    path('authors/<path:fid>/posts/', ProfilePostsView.as_view(), name='remote-profile-posts'),
    path('authors/<str:id>', ProfileView.as_view(), name='remote-getProfile'),
    path('authors/<path:id>/', ProfileView.as_view(), name='local-getProfile'),
    # path('authors/<str:uid>/commented/', views.AuthorCommentedUIDView.as_view(), name='author_uid_commented'), 
    # path('authors/<path:fqid>/commented/', views.AuthorCommentedFQIDView.as_view(), name='author_fqid_commented'), #local only
    # path('commented/<path:fqid>', views.AuthorCommentedView.as_view(), name='author_commented'), #local only
    # path('authors/<str:uid>/commented/<str:comment-uid>', views.AuthorCommentedCommentView.as_view(), name='author_commented_comment'),
    
    #likes api
    path('authors/<str:author_uid>/posts/<str:post_uid>/likes', authorPostLikesView, name='author_post_likes'),
    # path('posts/<str:post_uid>/likes', postLikesViewLocal, name='post_likes'), #local only
    path('authors/<str:author_uid>/posts/<str:post_uid>/comments/<str:comment_uid>/likes', authorPostCommentLikesView, name='author_post_comment_likes'),

    #liked api
    path('authors/<str:author_uid>/liked', allLikedUIDView, name='author_uid_all_liked'),
    path('authors/<str:author_uid>/liked/<str:like_uid>', likedView, name='author_liked'),
    # path('authors/<path:author_fqid>/liked', allLikedFQIDViewLocal, name='author_fqid_all_liked'), #local only
    # path('liked/<path:like_fqid>', justLikedViewLocal, name='liked'), #local only

    #didnt include local urls for now, too tired
    #comments api
    path('authors/<uuid:author_uid>/posts/<uuid:post_uid>/comments', getCommentsByPostIDView, name='get_comments'),
    path("posts/<path:post_fqid>/comments", getCommentsByPostFQIDView, name = "get_comments_by_post_fqid"),
    path('authors/<uuid:author_uid>/post/<uuid:post_uid>/comment/<path:comment_fqid>', getCommentByFQIDView, name='get_comment'),
    
    #commented api
    path('authors/<uuid:author_uid>/commented', getAllCommentsByAuthorByUIDView, name='get_author_comment'),
    path('authors/<uuid:author_uid>/commented/<uuid:comment_uid>', getCommentedCommentByUIDView, name='get_particular_comment'),


    #not sure if these are needed

    # path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/', dummy_view, name='get_local_comments'),
    # path('comment/<uuid:comment_id>/', dummy_view, name='get_single_comment'),
    
]