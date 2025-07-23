from django.urls import path
from .views import BlogView

urlpatterns = [
    path("blogs/", BlogView.as_view({"get":"list"}), name='blogs'),
    path("blogs/<int:pk>", BlogView.as_view({"get":"retrieve"}), name='blog-detail')
]