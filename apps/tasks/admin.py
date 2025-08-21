from django.contrib import admin

from apps.tasks.models import TimeLog


# Register your models here.
@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = (
        "task_id",
        "start_time",

        "end_time",
        "duration"
    )