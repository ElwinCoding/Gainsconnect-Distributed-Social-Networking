from django.urls import path, include
from .views import *

urlpatterns = [
    path('request/', FollowRequestView.as_view(), name='followRequest'),
    path('receive/<str:uid>', FollowRequestView.as_view(), name='receiveList'),
    path('list/<str:id>/<str:category>', ListFollower.as_view(), name='getList'),
    path('explore/<str:uid>', ExploreAuthors.as_view(), name='exploreAuthors'),
    path('request/reply/', HandleRequestView.as_view(), name="declineRequest")
]
