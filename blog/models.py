import os.path
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.utils.safestring import mark_safe
from core.models import TimeBase
from tinymce import models as tinymce_models


class BlogType(models.Model):
    typename = models.CharField(
        max_length=255,
        help_text="Blogni bo'limlarga ajratish uchun blog typelarini yarating"
    )

    class Meta:
        db_table = "blogtype"
        verbose_name = "Blog Type"

    def __str__(self):
        return self.typename


class Blog(TimeBase):
    title = models.CharField(max_length=255, null=True, blank=True)
    body = tinymce_models.HTMLField()
    type = models.ForeignKey(BlogType, on_delete=models.SET_NULL, null=True, blank=True)
    views = models.IntegerField(default=0)

    class Meta:
        db_table = 'blogs'
        verbose_name = 'Blog'

    def __str__(self):
        return self.title

    def photo_tag(self):
        first_image = self.images.first()
        if first_image and first_image.image:
            return mark_safe(f'<img src="{first_image.image.url}" width="200px" />')
        return "No Image"

class BlogImage(TimeBase):
    blog = models.ForeignKey(Blog, on_delete=models.SET_NULL, null=True, blank=True, related_name='images')
    image = models.ImageField(upload_to='blog_images/')

    class Meta:
        db_table = "blog_images"
        verbose_name = "Blog Images"

    def __str__(self):
        return str(self.blog)


    def save(self, *args, **kwargs):
        if self.image:
            original_name = self.image.name
            ext = os.path.splitext(original_name)[1].lower()

            if ext != ".webp":
                img = Image.open(self.image)
                img = img.convert("RGB")
                filename = os.path.splitext(self.image.name)[0] + ".webp"
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=80)
                self.image.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)