from django.urls import path
from .views import InboxView

urlpatterns = [
    path('authors/<str:uid>/inbox', InboxView.as_view(), name='inbox')
]
