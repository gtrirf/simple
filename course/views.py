from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from .serializers import CourseListSerializers, AboutCourseSerializer, CourseLearningPointSerializer, \
    CourseStatisticSerializer, StudentCertificateSerializers
from .models import AboutCourse, CourseStatistic, Course, CourseLearningPoint, StudentsCertificates

class CourseListView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseListSerializers(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CourseDetailView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseListSerializers(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AboutCourseListView(APIView):
    def get(self, request):
        about_courses = AboutCourse.objects.all()
        serializer = AboutCourseSerializer(about_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AboutCourseDetailView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        about = AboutCourse.objects.filter(course=course)
        serializer = AboutCourseSerializer(about, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CourseLearningPointView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        point = CourseLearningPoint.objects.filter(course=course)
        serializer = CourseLearningPointSerializer(point, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CourseStatisticView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        point = CourseStatistic.objects.filter(course=course)
        serializer = CourseStatisticSerializer(point, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentCertificatesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        certificate = get_object_or_404(StudentsCertificates)
        serializers = StudentCertificateSerializers(certificate, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

class StudentCertificateView(APIView):
    def get(self, request, uuid):
        certificate = get_object_or_404(StudentsCertificates, url_uuid=uuid)
        serializers = StudentCertificateSerializers(certificate)
        return Response(serializers.data, status=status.HTTP_200_OK)
