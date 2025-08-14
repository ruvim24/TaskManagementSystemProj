from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (TaskDetailsView, TaskListDetailsView, LastMontLoggedTimeDurationView, TasksListDurationView,
                    TopTasksLastMonthView, UploadFileView)
from django.views.decorators.cache import cache_page

router = DefaultRouter()
router.register(r'tasks', TaskDetailsView, basename='tasks')

urlpatterns = [
    path("list/", TaskListDetailsView.as_view(), name='task_list_details'),
    path('last-month-time-logged-duration/', LastMontLoggedTimeDurationView.as_view(),
         name='last_month_logged_time_duration'),
    path('duration/', TasksListDurationView.as_view(), name='tasks_list_duration'),
    path('top-tasks/', cache_page(60)(TopTasksLastMonthView.as_view()), name='top_tasks_last_month'),

    path('tasks/upload-webhook/', UploadFileView.as_view(), name='upload_webhook'),

    path('', include(router.urls)),

]
