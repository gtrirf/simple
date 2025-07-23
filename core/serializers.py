from rest_framework import serializers
from .models import Statistics, Leads, Faqs


class StatisticsSerializer(serializers.ModelSerializer):
        class Meta:
            model = Statistics
            fields = "__all__"


class LeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = ['fullname', 'phone_number', 'branches', 'is_online', 'is_offline', 'is_agree']


class FaqsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Faqs
        fields = '__all__'
