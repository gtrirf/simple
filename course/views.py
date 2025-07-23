from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from .serializers import CourseListSerializers, AboutCourseSerializer, CourseLearningPointSerializer, \
    CourseStatisticSerializer, StudentCertificateSerializers
from .models import AboutCourse, CourseStatistic, Course, CourseLearningPoint, StudentsCertificates
from rest_framework.permissions import AllowAny
from django.db.models import Q


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

    def get(self, request):
        full_name = request.GET.get('full_name')
        certificate_id = request.GET.get('certificate_id')

        filters = {}

        if full_name:
            try:
                first_name, last_name = full_name.strip().split(' ', 1)
                filters['first_name__iexact'] = first_name.strip()
                filters['last_name__iexact'] = last_name.strip()
            except ValueError:
                return Response({"error": "To‘liq ism-familya kiriting"}, status=status.HTTP_400_BAD_REQUEST)

        if certificate_id:
            filters['certificate_id__iexact'] = certificate_id.strip()

        if not filters:
            return Response({"error": "Kamida full_name yoki certificate_id kerak"}, status=status.HTTP_400_BAD_REQUEST)

        certificate = StudentsCertificates.objects.filter(**filters).first()

        if not certificate:
            return Response({"error": "Sertifikat topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentCertificateSerializers(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentCertificateView(APIView):
    def get(self, request, uuid):
        certificate = get_object_or_404(StudentsCertificates, url_uuid=uuid)
        serializers = StudentCertificateSerializers(certificate)
        return Response(serializers.data, status=status.HTTP_200_OK)
