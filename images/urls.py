from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
from .views import PostImageAPIView, GetUsersImagesAPIView, ExpirationLinkAPIView

urlpatterns = [
    path('api/post-image', PostImageAPIView.as_view({'post': 'retrieve'})),
    path('api/get-users-images', GetUsersImagesAPIView.as_view({'get': 'retrieve'})),
    path('api/expiration-link', ExpirationLinkAPIView.as_view({'post': 'retrieve'})),
    path('api/token-auth', views.obtain_auth_token),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
