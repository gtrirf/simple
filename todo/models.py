from core.models import TimeBase, CustomUser
from course.models import CourseName
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from datetime import date

User = get_user_model()

class Rooms(models.Model):
    room_name = models.CharField(max_length=255)

    def __str__(self):
        return self.room_name


class Guruhlar(models.Model):
    WEEKDAY_CHOICES = [
        ("toq_kunlar", "Du-Chor-Ju"),
        ("juft_kunlar", "Se-Pay-Shan"),
        ('se_yak', "Se-Yak"),
        ("har_kun", "Ish kunlari")
    ]
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey("Teacher", on_delete=models.SET_NULL, null=True)
    students_count = models.PositiveIntegerField()
    week_days = models.CharField(max_length=100, choices=WEEKDAY_CHOICES, null=True, blank=True)
    room = models.ForeignKey(Rooms, on_delete=models.SET_NULL, null=True, blank=True)
    lesson_time = models.TimeField()
    lesson_end_time = models.TimeField()

    def __str__(self):
        return self.name

class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    subject = models.ForeignKey(CourseName, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(models.Model):
    date = models.DateField(auto_now_add=True)
    group = models.ForeignKey(Guruhlar, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    student_attended = models.PositiveIntegerField()

    class Meta:
        unique_together = ['date', 'group']

    def __str__(self):
        return f"{self.group.name} - {self.date}"

    @property
    def student_absent(self):
        return self.group.students_count - self.student_attended


class VisitorLog(models.Model):
    VISITOR_TYPE_CHOICES = [
        ('student', 'O‘quvchi'),
        ('new', 'Yangi mijoz'),
        ('parent', 'Ota-ona'),
        ('other', 'Boshqa')
    ]
    date = models.DateField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    visitor_type = models.CharField(max_length=10, choices=VISITOR_TYPE_CHOICES)
    purpose = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.visitor_type}) - {self.date}"


class Task(models.Model):
    class RepetitionChoices(models.TextChoices):
        NONE = 'none', _('No Repeat')
        DAILY = 'daily', _('Daily')
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        IN_PROGRESS = 'in_progress', _('In Progress')
        DONE = 'done', _('Done')
        CANCELLED = 'cancelled', _('Cancelled')

    class PriorityChoices(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True) # deadline uchun
    repetition = models.CharField(
        max_length=10,
        choices=RepetitionChoices.choices,
        default=RepetitionChoices.NONE,
    ) # takroriy jo'natish uchun
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    ) # task holat uchun
    priority = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
    )
    assigned_to = models.ManyToManyField(User, related_name="assigned_tasks")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tasks")
    is_active = models.BooleanField(default=True)
    sending_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.due_date or 'No deadline'}"

    def is_overdue(self):
        return self.due_date and date.today() > self.due_date

    class Meta:
        ordering = ['-created_at']


class TaskComment(TimeBase):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField()

    def __str__(self):
        uname = getattr(self.user, 'fullname', None) or getattr(self.user, 'username', 'Unknown user')
        return f"{uname} – {self.task.title}"


class Staff_attendance(TimeBase):
    objects = None

    class StatusChoices(models.TextChoices):
        IN_CLASS = 'in_class', _("📘 Darsda")
        ON_LUNCH = 'on_lunch', _('🍽 Tushlikda')
        NOT_AT_OFFICE = 'not_at_office', _("🏠 Ishda emas")
        AVAILABLE = 'available', _("✅ Ishda")
        BUSY = 'busy', _('🔴 Band')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE,
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Staff Attendance"