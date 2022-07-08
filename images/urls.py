from django.urls import path
from .views import PostImageAPIView

urlpatterns = [
    path('api/post-image', PostImageAPIView.as_view({'post': 'retrieve'})),
]