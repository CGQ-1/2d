from django.contrib.admin.models import LogEntry
from django.contrib import admin

from .models import Link, Sidebar
from typeidea2.custom_site import custom_site
from typeidea2.base_admin import BaseOwnerAdmin


@admin.register(Link)
class LinkAdmin(BaseOwnerAdmin):
    list_display = ('title', 'href', 'status', 'weight', 'created_time')
    fields = ('title', 'href', 'status', 'weight')


@admin.register(Sidebar)
class SidebarAdmin(BaseOwnerAdmin):
    list_display = ('title', 'display_type', 'content', 'created_time')
    fields = ('title', 'display_type', 'content')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']