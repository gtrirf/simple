from django.contrib import admin
from .models import Course, AboutCourse, CourseLearningPoint, CourseStatistic

class AboutCourseInline(admin.TabularInline):
    model = AboutCourse
    extra = 1
    fields = ('title', 'body')
    show_change_link = True

class CourseLearningPointInline(admin.TabularInline):
    model = CourseLearningPoint
    extra = 1
    fields = ('point',)
    show_change_link = True

class CourseStatisticInline(admin.TabularInline):
    model = CourseStatistic
    extra = 1
    fields = ('graduated_students', 'busy', 'cheapest_salary', 'highest_salary')
    show_change_link = True

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'price', 'duration_month', 'weeks', 'hours', 'thumbnail', 'intro_video_url')
    search_fields = ('name', 'level')
    list_filter = ('level',)
    inlines = [AboutCourseInline, CourseLearningPointInline, CourseStatisticInline]
    ordering = ['name']
    list_per_page = 10

@admin.register(AboutCourse)
class AboutCourseAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'body')
    search_fields = ('course__name', 'title')
    list_filter = ('course',)
    ordering = ['course']

@admin.register(CourseLearningPoint)
class CourseLearningPointAdmin(admin.ModelAdmin):
    list_display = ('course', 'point')
    search_fields = ('course__name', 'point')
    list_filter = ('course',)
    ordering = ['course']

@admin.register(CourseStatistic)
class CourseStatisticAdmin(admin.ModelAdmin):
    list_display = ('graduated_students', 'busy', 'cheapest_salary', 'highest_salary')
    search_fields = ('graduated_students', 'cheapest_salary', 'highest_salary')
    list_filter = ('graduated_students',)
    ordering = ['graduated_students']


from django.contrib import admin
from django.template.response import TemplateResponse
import openpyxl
from .models import CourseName, StudentsCertificates
import uuid
from django.shortcuts import redirect
from django.urls import path
from django import forms
from django.contrib import messages


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()



@admin.register(CourseName)
class CourseNameAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(StudentsCertificates)
class StudentCertificateAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'course_name', 'certificate_id']
    list_filter = ['course_name']
    search_fields = ['first_name', 'last_name', 'certificate_id']
    change_list_template = "admin/students_certificates_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel_view)
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        if request.method == "POST":
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = form.cleaned_data["excel_file"]

                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active

                added = 0

                for row in ws.iter_rows(min_row=2):  # headerdan keyin
                    first_name = row[0].value
                    last_name = row[1].value
                    course_name_val = row[2].value
                    certificate_id = row[3].value
                    cert_cell = row[4]

                    if not certificate_id:
                        continue

                    if cert_cell.hyperlink:
                        url = cert_cell.hyperlink.target
                    else:
                        url = ""

                    # dublikatni tekshir
                    if StudentsCertificates.objects.filter(certificate_id=certificate_id).exists():
                        continue

                    course_obj, _ = CourseName.objects.get_or_create(name=course_name_val)

                    StudentsCertificates.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        course_name=course_obj,
                        url_uuid=uuid.uuid4().hex[:16],
                        certificate_id=certificate_id,
                        certificate_url=url
                    )
                    added += 1

                self.message_user(request, f"{added} ta yozuv muvaffaqiyatli qo‘shildi!", level=messages.SUCCESS)
                return redirect("..")
        else:
            form = ExcelImportForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        return TemplateResponse(request, "admin/excel_upload.html", context)
