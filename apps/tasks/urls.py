from django.urls import path
from .views import (
    TaskDetailsView, CreateTaskView,
    TaskListDetailsView, TaskListView,
    AssignUserToTask, CompleteTaskView,
    RemoveTaskView, AddCommentToTask, TaskCommentsView)

urlpatterns = [
    path("<int:pk>", TaskDetailsView.as_view(), name='task_item'),
    path("", CreateTaskView.as_view(), name='create_task'),
    path("list-details/", TaskListDetailsView.as_view(), name='task_list_details'),

    path("list/", TaskListView.as_view(), name='task_list'),

    path("<int:pk>/asign-user/", AssignUserToTask.as_view(), name='asign_user_to_task'),
    path("<int:pk>/complete/", CompleteTaskView.as_view(), name='complete_task'),
    path("<int:pk>/", RemoveTaskView.as_view(), name='remove_task'),

    path("<int:pk>/comment/", AddCommentToTask.as_view(), name='add_comment_to_task'),

    path("<int:pk>/comments/", TaskCommentsView.as_view(), name='task_comments')

]
