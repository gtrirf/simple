from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.username


class TimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Statistics(models.Model):
    all_students = models.IntegerField(verbose_name='Number of all students', help_text="jami bitiruvchilar sonini kiriting")
    experience = models.IntegerField(verbose_name="Years of experience", help_text="Tajriba yilini kiriting")
    num_branches = models.IntegerField(verbose_name="Number of branches", help_text="Filiallar sonini kiriting")
    num_staff = models.IntegerField(verbose_name="Number of employees", help_text="Xodimlar sonini kiriting")

    class Meta:
        db_table = "statistics"
        verbose_name = "Statistic"

    def __str__(self):
        return "Statistics of Devops IT CENTER"


class Leads(TimeBase):
    from course.models import CourseName
    class Branches(models.TextChoices):
        KRUG = 'krug', _("Krug Filiali")
        PARK = 'Park', _('Park Filiali')

    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    branches = models.CharField(max_length=100, choices=Branches, default=Branches.KRUG)
    models.ForeignKey(CourseName, on_delete=models.SET_NULL, null=True, blank=True)
    is_online = models.BooleanField(default=False)
    is_offline =models.BooleanField(default=False)
    is_agree = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'leads'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self):
        return self.fullname


from django.db import models


class Faqs(models.Model):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'faqs'
        verbose_name = "Faq"

    def __str__(self):
        return self.title

