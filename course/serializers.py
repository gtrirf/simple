from rest_framework import serializers
from .models import Course, AboutCourse, CourseLearningPoint, CourseStatistic, StudentsCertificates


class CourseListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id",'name', 'description', 'duration_month', "weeks", "hours", "price", 'level', 'thumbnail', "intro_video_url"]


class AboutCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutCourse
        fields = ["course", 'title', 'body']


class CourseLearningPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLearningPoint
        fields = ['point']


class CourseStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatistic
        fields = ['graduated_students', 'busy', 'cheapest_salary', 'highest_salary']


class CourseDetailSerializer(serializers.ModelSerializer):
    # Handle statistics, learning points, and about as many-to-one or many-to-many
    learning_points = CourseLearningPointSerializer(many=True, source='courselearningpoint_set')
    about = AboutCourseSerializer(many=True, source='aboutcourse_set')
    statistics = CourseStatisticSerializer(allow_null=True, required=False, source='statistics_for_course')

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'duration_month', 'weeks', 'hours', 'price', 'level',
            'thumbnail', 'intro_video_url', 'about', 'learning_points', 'statistics'
        ]


class StudentCertificateSerializers(serializers.ModelSerializer):
    class Meta:
        model = StudentsCertificates
        fields = "__all__"
