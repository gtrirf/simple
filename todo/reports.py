from .models import VisitorLog, Guruhlar
from django.db.models import Sum, Count
from datetime import date, timedelta
from .models import Attendance

# 🔹 Oylik hisobot (jami statistikasi)
def get_filtered_report(from_date, to_date):
    attendance = Attendance.objects.filter(date__range=[from_date, to_date])
    visitor_logs = VisitorLog.objects.filter(date__range=[from_date, to_date])

    total_groups = Guruhlar.objects.count()
    total_students = sum(g.students_count for g in Guruhlar.objects.all())

    attended = attendance.aggregate(Sum('student_attended'))['student_attended__sum'] or 0
    expected = sum([a.group.students_count for a in attendance if a.group])
    absent = expected - attended

    visitor_counts = visitor_logs.values('visitor_type').annotate(count=Count('id'))
    visitor_data = {
        'student': 0,
        'new': 0,
        'parent': 0,
        'other': 0,
        'total': visitor_logs.count()
    }
    for item in visitor_counts:
        visitor_data[item['visitor_type']] = item['count']

    return {
        "from": from_date,
        "to": to_date,
        "total_groups": total_groups,
        "total_students": total_students,
        "total_absent": absent,
        "visitor_data": visitor_data
    }

def get_today_report():
    today = date.today()
    return get_filtered_report(today, today)