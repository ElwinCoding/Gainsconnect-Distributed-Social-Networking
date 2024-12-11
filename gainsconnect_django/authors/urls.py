from django.urls import path, include
from .views import *
from . import views
#from .views import get_github_usernames
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path('updateProfile/', UpdateProfileView.as_view(), name='update_profile'),
    path('github_usernames/', get_github_usernames, name='github_usernames'),
    path("service/api/authors/", PaginatedAuthorsView.as_view(), name="paginated_authors"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
