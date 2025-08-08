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
        full_name = request.GET.get('fullname')
        certificate_id = request.GET.get('certificate_id')

        # Ikkisi ham berilmagan holat
        if not full_name and not certificate_id:
            return Response({"error": "Kamida fullname yoki certificate_id kerak"}, status=status.HTTP_400_BAD_REQUEST)

        certificate = None

        # Faqat full_name berilgan holat
        if full_name and not certificate_id:
            try:
                first_name, last_name = full_name.strip().split(' ', 1)
                certificate = StudentsCertificates.objects.filter(
                    first_name__iexact=first_name.strip(),
                    last_name__iexact=last_name.strip()
                ).first()
            except ValueError:
                return Response({"error": "To'liq ism-familya kiriting"}, status=status.HTTP_400_BAD_REQUEST)

        # Faqat certificate_id berilgan holat
        elif certificate_id and not full_name:
            certificate = StudentsCertificates.objects.filter(
                certificate_id__iexact=certificate_id.strip()
            ).first()

        # Ikkisi ham berilgan holat
        else:
            try:
                first_name, last_name = full_name.strip().split(' ', 1)

                # Avval certificate_id bo'yicha qidiramiz
                cert_by_id = StudentsCertificates.objects.filter(
                    certificate_id__iexact=certificate_id.strip()
                ).first()

                # Agar certificate_id bo'yicha topilsa
                if cert_by_id:
                    # Ism-familya ham mos kelishini tekshiramiz
                    if (cert_by_id.first_name.lower() == first_name.strip().lower() and
                            cert_by_id.last_name.lower() == last_name.strip().lower()):
                        certificate = cert_by_id
                    else:
                        # ID to'g'ri lekin ism-familya xato - natija chiqmasin
                        certificate = None
                else:
                    # Certificate_id xato bo'lsa, ism-familyaga mos certificate qidiramiz
                    certificate = StudentsCertificates.objects.filter(
                        first_name__iexact=first_name.strip(),
                        last_name__iexact=last_name.strip()
                    ).first()

            except ValueError:
                return Response({"error": "To'liq ism-familya kiriting"}, status=status.HTTP_400_BAD_REQUEST)

        if not certificate:
            return Response({"error": "Sertifikat topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentCertificateSerializers(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentCertificateView(APIView):
    def get(self, request, uuid):
        certificate = get_object_or_404(StudentsCertificates, url_uuid=uuid)
        serializers = StudentCertificateSerializers(certificate)
        return Response(serializers.data, status=status.HTTP_200_OK)
