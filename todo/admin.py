from datetime import date
from django.contrib import admin
from .models import Attendance, Teacher, Guruhlar, VisitorLog, Rooms, Task, Staff_attendance
from django.contrib import admin, messages
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from .reports import get_today_report, get_filtered_report
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Staff_attendance, CustomUser
from datetime import datetime, timedelta


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


@admin.register(Staff_attendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'attendance-report/',
                self.attendance_report_view,
                name='attendance_report'
            ),
            path(
                'attendance-report/<int:user_id>/',
                self.user_attendance_detail,
                name='user_attendance_detail'
            ),
        ]
        return custom_urls + urls

    def attendance_report_view(self, request):
        # Bugungi sana
        today = timezone.now().date()

        # Bugun davomat belgilagan userlar
        users = CustomUser.objects.filter(
            staff_attendance__created_at__date=today
        ).distinct().order_by('first_name', 'last_name')

        context = {
            'title': 'Davomat Statistikasi',
            'users': users,
            'today': today,
            'opts': self.model._meta,
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'has_permission': True,
        }
        return render(request, 'admin/attendance_report.html', context)

    def user_attendance_detail(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        today = timezone.now().date()

        # Bugungi davomat rekordlari
        attendance_records = Staff_attendance.objects.filter(
            user=user,
            created_at__date=today
        ).order_by('created_at')

        # Statistikani hisoblash
        status_times = self.calculate_status_times(attendance_records)

        context = {
            'title': f'{user.first_name} {user.last_name} - Davomat Tafsilotlari',
            'user': user,
            'today': today,
            'records': attendance_records,
            'status_times': status_times,
            'opts': self.model._meta,
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'has_permission': True,
            'timezone': timezone,  # Template uchun timezone obyekti
        }
        return render(request, 'admin/user_attendance_detail.html', context)

    def calculate_status_times(self, records):
        if not records.exists():
            return {
                'available': '0:00:00',
                'in_class': '0:00:00',
                'busy': '0:00:00',
                'on_lunch': '0:00:00',
                'not_at_office': '0:00:00',
                'total_work': '0:00:00',
                'total_away': '0:00:00',
            }

        # Statuslar bo'yicha vaqtlarni hisoblash
        status_times = {
            'available': timedelta(),
            'in_class': timedelta(),
            'busy': timedelta(),
            'on_lunch': timedelta(),
            'not_at_office': timedelta(),
        }

        records_list = list(records)  # QuerySet ni list ga aylantirish

        # Har bir status o'zgarishi orasidagi vaqtni hisoblash
        for i in range(len(records_list) - 1):
            current = records_list[i]
            next_rec = records_list[i + 1]
            duration = next_rec.created_at - current.created_at
            if current.status in status_times:
                status_times[current.status] += duration

        # Oxirgi rekorddan hozirgacha bo'lgan vaqt
        if records_list:
            last_record = records_list[-1]
            now = timezone.now()
            # Agar oxirgi record bugun bo'lsa
            if last_record.created_at.date() == timezone.now().date():
                last_duration = now - last_record.created_at
                if last_record.status in status_times:
                    status_times[last_record.status] += last_duration

        # Formatlash
        formatted_times = {}
        for status, td in status_times.items():
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_times[status] = f"{hours}:{minutes:02d}:{seconds:02d}"

        # Umumiy ish vaqti (not_at_office dan tashqari hammasi)
        total_work_time = sum([
            status_times['available'],
            status_times['in_class'],
            status_times['busy'],
            status_times['on_lunch']
        ], timedelta())
        total_seconds = int(total_work_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_times['total_work'] = f"{hours}:{minutes:02d}:{seconds:02d}"

        # Abetgan vaqt (not_at_office)
        formatted_times['total_away'] = formatted_times['not_at_office']

        return formatted_times