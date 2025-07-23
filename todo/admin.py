from datetime import date
from django.contrib import admin
from .models import Attendance, Teacher, Guruhlar, VisitorLog, Rooms, Task
from django.contrib import admin, messages
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from .reports import get_today_report, get_filtered_report

admin.site.register(Rooms)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "phone", 'subject']
    list_filter = ['subject']
    search_fields = ['first_name', "last_name", "phone"]


@admin.register(Guruhlar)
class GuruhlarAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'students_count', 'week_days', "room", "lesson_time", "lesson_end_time"]
    list_filter = ['name', 'lesson_time', 'teacher', "room", "week_days"]
    search_fields = ['name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'group', 'teacher', 'student_attended', 'student_absent')
    list_filter = ('date', 'group', 'teacher')
    search_fields = ('group__name', 'teacher__full_name')


@admin.register(VisitorLog)
class VisiterLogAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'visitor_type', 'phone', 'date')
    list_filter = ('visitor_type', 'date')
    search_fields = ('full_name', 'phone')
    change_list_template = "admin/link.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-report/', self.admin_report_view, name="custom-report"),
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def admin_report_view(self, request):
        today_report = get_today_report()

        from_date = request.GET.get("from")
        to_date = request.GET.get("to")
        filtered_report = None

        if from_date and to_date:
            from_date_parsed = date.fromisoformat(from_date)
            to_date_parsed = date.fromisoformat(to_date)
            filtered_report = get_filtered_report(from_date_parsed, to_date_parsed)

        context = dict(
            self.admin_site.each_context(request),
            today=today_report,
            filtered=filtered_report,
            from_date=from_date,
            to_date=to_date
        )
        return TemplateResponse(request, "admin/reports.html", context)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "get_assigned_users", "due_date", "repetition", "status", "priority", "is_active")
    list_filter = ("status", "priority", "repetition", "is_active")
    search_fields = ("title", "description", "assigned_to__username")
    filter_horizontal = ("assigned_to",)
    autocomplete_fields = ("created_by",)

    def get_assigned_users(self, obj):
        return ", ".join([user.username for user in obj.assigned_to.all()])

    get_assigned_users.short_description = "Assigned Users"
