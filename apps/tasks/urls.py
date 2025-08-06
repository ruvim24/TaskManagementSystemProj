from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (TaskDetailsView, TaskListDetailsView)

router = DefaultRouter()
router.register(r'', TaskDetailsView)

urlpatterns = [
    path('', include(router.urls)),
    path("list-details/", TaskListDetailsView.as_view(), name='task_list_details'),
]
