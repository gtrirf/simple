from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Statistics, Leads, Faqs


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Telegram Info', {
            'fields': ['telegram_id'],
        }),
    )
    list_display = ('username', 'email', 'telegram_id', 'is_staff')


@admin.register(Statistics)
class AdminStatistics(admin.ModelAdmin):
    list_display = ["all_students", "experience", "num_branches", "num_staff"]


@admin.register(Leads)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["fullname", "phone_number", "is_online", "is_offline", 'is_agree', "is_connected"]
    list_filter = ["is_online", "is_offline", "is_agree", "is_connected"]
    search_fields = ['fullname', "phone_number"]


@admin.register(Faqs)
class FaqsAdmin(admin.ModelAdmin):
    list_display = ['title', "description"]
    list_filter = ['title']
    search_fields = ['title', "description"]