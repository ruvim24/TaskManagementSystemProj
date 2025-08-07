from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (TaskDetailsView, TaskListDetailsView, LastMontLoggedTimeDurationView, TasksListDurationView,
                    TopTasksLastMonthView)

router = DefaultRouter()
router.register(r'', TaskDetailsView)

urlpatterns = [
    path("list/", TaskListDetailsView.as_view(), name='task_list_details'),
    path('last-month-time-logged-duration', LastMontLoggedTimeDurationView.as_view(),
         name='last_month_logged_time_duration'),
    path('duration/', TasksListDurationView.as_view(), name='tasks_list_duration'),
    path('top-tasks/', TopTasksLastMonthView.as_view(), name='top_tasks_last_month'),
    path('', include(router.urls)),

]
