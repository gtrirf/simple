from django.core.management.base import BaseCommand
from course.models import CourseName  # to‘g‘ri path yoz

class Command(BaseCommand):
    help = 'Automatically generates CourseName entries'

    def handle(self, *args, **kwargs):
        course_list = [
            "Kompyuter savodxonligi",
            "Frond End",
            "Grafik va web dizayn",
            "3D Max",
            "Ingliz tili",
            "SSV malaka oshirish",
            "DX malaka oshirish",
            "DX malaka oshirish",
            "Android dasturlash",
            "KS va Xalqaro IT Serrifikat",
            "Backend dasturlash"
        ]

        created = 0
        for name in course_list:
            obj, is_created = CourseName.objects.get_or_create(name=name)
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} ta yangi kurs qo‘shildi."))
