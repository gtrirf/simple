from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Statistics


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Telegram Info', {
            'fields': ('telegram_id', 'status'),
        }),
    )
    list_display = ('username', 'email', 'telegram_id', 'status', 'is_staff')
    list_filter = ('status',)


@admin.register(Statistics)
class AdminStatistics(admin.ModelAdmin):
    list_display = ["all_students", "experience", "num_branches", "num_staff"]

