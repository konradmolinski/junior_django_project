from django.urls import path
from .views import PostImageAPIView, GetUsersImagesAPIView
from rest_framework.authtoken import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/post-image', PostImageAPIView.as_view({'post': 'retrieve'})),
    path('api/get-users-images', GetUsersImagesAPIView.as_view({'get': 'retrieve'})),
    path('api/token-auth', views.obtain_auth_token),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
