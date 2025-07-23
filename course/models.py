import os
import uuid
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from core.models import TimeBase


class Course(TimeBase):
    LEVEL_CHOICES = [
        ('bootcamp', 'Bootcamp'),
        ('standard', 'standard'),
        ('online', 'Online'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    duration_month = models.IntegerField(null=True, blank=True)
    weeks = models.IntegerField(null=True, blank=True)
    hours = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)
    intro_video_url = models.CharField(
        max_length=400, null=True, blank=True, help_text="Tanishtiruvchi video uchun YouTube havolasi"
    )

    class Meta:
        db_table = 'course'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.thumbnail:
            original_name = self.thumbnail.name
            ext = os.path.splitext(original_name)[1].lower()

            if ext != ".webp":
                img = Image.open(self.thumbnail)
                img = img.convert("RGB")
                filename = os.path.splitext(self.thumbnail.name)[0] + ".webp"
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=80)
                self.thumbnail.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

class AboutCourse(TimeBase):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='aboutcourse_set')
    title = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField()

    class Meta:
        db_table = 'aboutcourse'

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class CourseLearningPoint(TimeBase):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='courselearningpoint_set')
    point = models.TextField(help_text="Kursda o‘rganiladigan asosiy bilim yoki ko‘nikma")


class CourseStatistic(TimeBase):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True,blank=True, related_name='statistics_for_course')
    graduated_students = models.IntegerField()
    busy = models.IntegerField(null=True, blank=True)
    cheapest_salary = models.IntegerField(null=True, blank=True)
    highest_salary = models.IntegerField(null=True, blank=True)


class CourseName(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kurs nomi")

    class Meta:
        db_table = "course_name"
        verbose_name = "Course Name"
        verbose_name_plural = "Course Names"

    def __str__(self):
        return self.name


class StudentsCertificates(TimeBase):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.ForeignKey(CourseName, on_delete=models.SET_NULL, null=True, blank=True)
    url_uuid = models.CharField(max_length=16, unique=True, help_text="bu yerga hc nima kiritmang!")
    certificate_id = models.CharField(max_length=100, unique=True, help_text="Serifikat id raqamini kiriting")
    certificate_url = models.TextField(help_text="Sertifikat joylashgan public urlni qo'ying")

    class Meta:
        db_table = "student_certificates"
        verbose_name = "Student Certificate"

    def save(self, *args, **kwargs):
        self.url_uuid = uuid.uuid4().hex[:16]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.certificate_id
