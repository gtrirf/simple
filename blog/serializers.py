from rest_framework import serializers
from .models import Blog, BlogImage, BlogType


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['id', 'image']

class BlogSerializer(serializers.ModelSerializer):
    images = BlogImageSerializer(many=True, read_only=True)
    type = serializers.SlugRelatedField(
        slug_field='typename',
        queryset=BlogType.objects.all()
    )

    class Meta:
        model = Blog
        fields = ['id', 'title', 'body', 'type', 'views', 'images', 'created_at']