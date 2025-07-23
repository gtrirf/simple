from django.urls import path
from .views import StatisticsView, LeadsAPIView, FaqsViews

urlpatterns = [
    path("statistics/", StatisticsView.as_view({"get":'list'}), name='statistics'),
    path("statistics/<int:pk>", StatisticsView.as_view({"get":"retrieve"}), name='statistics-detail'),
    path('leads/', LeadsAPIView.as_view(), name='lead-create'),
    path('faqs/', FaqsViews.as_view({'get': 'list'}), name='faqs-list'),
    path('faqs/<int:pk>/', FaqsViews.as_view({'get': 'retrieve'}), name='faqs-retrieve')
]