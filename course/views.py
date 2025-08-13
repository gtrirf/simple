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


from django.db.models import Q

class StudentCertificatesView(APIView):

    def get(self, request):
        full_name = request.GET.get('fullname')
        certificate_id = request.GET.get('certificate_id')

        if not full_name and not certificate_id:
            return Response({"error": "Kamida fullname yoki certificate_id kerak"}, status=status.HTTP_400_BAD_REQUEST)

        certificate = None
        part1 = part2 = None

        if full_name:
            parts = full_name.strip().split(' ', 1)
            if len(parts) != 2:
                return Response({"error": "To'liq ism-familya kiriting"}, status=status.HTTP_400_BAD_REQUEST)
            part1, part2 = parts[0].strip(), parts[1].strip()

        # Faqat certificate_id
        if certificate_id and not full_name:
            certificate = StudentsCertificates.objects.filter(
                certificate_id__iexact=certificate_id.strip()
            ).first()

        # Faqat fullname
        elif full_name and not certificate_id:
            certificate = StudentsCertificates.objects.filter(
                (Q(first_name__iexact=part1) & Q(last_name__iexact=part2)) |
                (Q(first_name__iexact=part2) & Q(last_name__iexact=part1))
            ).first()

        # Ikkalasi ham berilgan
        elif certificate_id and full_name:
            # Avval ID bo‘yicha qidiramiz
            cert_by_id = StudentsCertificates.objects.filter(
                certificate_id__iexact=certificate_id.strip()
            ).first()

            if cert_by_id:
                # ID topilgan bo‘lsa, fullname ham mos bo‘lishi kerak
                if (
                        (
                            cert_by_id.first_name.lower() == part1.lower() and cert_by_id.last_name.lower() == part2.lower()) or
                        (
                            cert_by_id.first_name.lower() == part2.lower() and cert_by_id.last_name.lower() == part1.lower())
                ):
                    certificate = cert_by_id
                else:
                    # ID to‘g‘ri, lekin ism-familya mos emas → natija yo‘q
                    certificate = None
            else:
                # ID topilmasa fullname bo‘yicha ikkala tartibda qidiramiz
                certificate = StudentsCertificates.objects.filter(
                    (Q(first_name__iexact=part1) & Q(last_name__iexact=part2)) |
                    (Q(first_name__iexact=part2) & Q(last_name__iexact=part1))
                ).first()

        if not certificate:
            return Response({"error": "Sertifikat topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentCertificateSerializers(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)




class StudentCertificateView(APIView):
    def get(self, request, uuid):
        certificate = get_object_or_404(StudentsCertificates, url_uuid=uuid)
        serializers = StudentCertificateSerializers(certificate)
        return Response(serializers.data, status=status.HTTP_200_OK)
