from django.urls import path
from .views import (CourseListView, AboutCourseListView,
                    CourseLearningPointView, CourseDetailView,
                    AboutCourseDetailView, CourseStatisticView, StudentCertificateView, StudentCertificatesView
                    )

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list'),
    path("course/<int:pk>", CourseDetailView.as_view(), name="course-detail"),
    path('courses/about/', AboutCourseListView.as_view(), name='course-about'),
    path("course/about/<int:pk>", AboutCourseDetailView.as_view(), name='about'),
    path("course/lp/<int:pk>", CourseLearningPointView.as_view(), name="course learning piont"),
    path("course/statistics/<int:pk>", CourseStatisticView.as_view(), name="course statistic piont"),
    path("certificate/<str:uuid>", StudentCertificateView.as_view(), name='certificate'),
    path("certificates/", StudentCertificatesView.as_view(), name='certifacates')
]
