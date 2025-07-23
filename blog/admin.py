from django.contrib import admin
from .models import Blog, BlogType, BlogImage
from tinymce.widgets import TinyMCE
from django import forms


class BlogForm(forms.ModelForm):
    body = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows': 10}))

    class Meta:
        model = Blog
        fields = '__all__'


class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogForm
    list_display = ('title', 'photo_tag', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('title', 'body')
    inlines = [BlogImageInline]


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('typename',)
    search_fields = ('typename',)


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('blog', 'image')
    list_filter = ('blog',)
