from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework import viewsets, status
from .serializers import StatisticsSerializer, LeadsSerializer, FaqsSerializers
from .models import Statistics, Faqs
import time


class StatisticsView(viewsets.ReadOnlyModelViewSet):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer


class LeadsAPIView(APIView):
    throttle_classes = [AnonRateThrottle]
    @extend_schema(
        request=LeadsSerializer,
        responses={201: LeadsSerializer},
        description="Create a new lead"
    )
    def post(self, request, *args, **kwargs):
        time.sleep(1.5)
        serializer = LeadsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FaqsViews(viewsets.ReadOnlyModelViewSet):
    queryset = Faqs.objects.all()
    serializer_class = FaqsSerializers


