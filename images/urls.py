from django.urls import path
from .views import PostImageAPIView
from rest_framework.authtoken import views


urlpatterns = [
    path('api/post-image', PostImageAPIView.as_view({'post': 'retrieve'})),
    path('api/token-auth', views.obtain_auth_token),
]