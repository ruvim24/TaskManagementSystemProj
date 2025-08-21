from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.tasks.factories import TaskFactory, CommentFactory, TimeLogFactory
from apps.tasks.models import Task, Comment


# Create your tests here.
class TaskTests(TestCase):
    def setUp(self) -> None:
        pass

    def test_task_get(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        # act
        response = client.get(f'/api/tasks/{task.id}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_list(self):
        # arrange
        client = APIClient()

        TaskFactory.create_batch(10)

        # act
        url = reverse('tasks-list')
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_task_create(self):
        # arrange
        client = APIClient()

        data = {"title": "test title", "description": "test description", "status": "open"}
        response = client.post('/api/tasks/', data=data, format='json')

        # act
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["description"], "test description")
        self.assertEqual(response.data["status"], "open")

    def test_task_update(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()
        update_data = {"title": "test title", "description": "test description", "status": "completed"}

        # act
        response = client.put(f'/api/tasks/{task.id}/', update_data, format='json')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["description"], "test description")
        self.assertEqual(response.data["status"], "completed")

    def test_task_delete(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        # act
        response = client.delete(f'/api/tasks/{task.id}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.filter(id=task.id).exists(), False)

    def test_task_complete(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        # act
        response = client.put(f'/api/tasks/{task.id}/complete/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).status, "completed")

    def test_task_create_comment(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        # act
        response = client.post(f'/api/tasks/{task.id}/comment/', {"comment": "test comment"}, format='json')

        # assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Comment.objects.get(id=response.data['comment_id']).content,
            "test comment"
        )
        self.assertEqual(
            Comment.objects.get(id=response.data['comment_id']).task.id,
            Task.objects.get(id=task.id).id
        )

    def test_task_get_comments(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()
        CommentFactory.create_batch(10, task=task)

        # act
        response = client.get(f'/api/tasks/{task.id}/comments/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_start_timer_should_be_successfully(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        # act
        response = client.post(f'/api/tasks/{task.id}/start-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_start_timer_should_fail(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()
        TimeLogFactory.create(task=task, start_time=datetime.now(), end_time=None)

        # act
        response = client.post(f'/api/tasks/{task.id}/start-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stop_timer_should_fail(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        # act
        response = client.put(f'/api/tasks/{task.id}/stop-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stop_timer_should_be_successfully(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()
        TimeLogFactory.create(
            task=task,
            start_time=datetime.now(),
            end_time=None,
            duration=None)

        # act
        response = client.put(f'/api/tasks/{task.id}/stop-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_get_time_logs_should_be_successfully(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        TimeLogFactory.create_batch(10, task=task)

        # act
        response = client.get(f'/api/tasks/{task.id}/time-logs/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_log_time_should_be_successfully(self):
        client = APIClient()
        task = TaskFactory.create()

        request_data = {
            'start_time': '2025-07-22T10:30:00Z',
            'end_time': '2025-07-22T10:30:00Z',
            'duration': 0
        }

        # act
        response = client.post(f'/api/tasks/{task.id}/log-time/', request_data, format='json')

        # assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_time_duration_should_be_successfully(self):
        client = APIClient()
        task = TaskFactory.create()
        TimeLogFactory.create_batch(2, task=task, duration=60)

        # act
        response = client.get(f'/api/tasks/{task.id}/logged-time-duration/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Total logged time in hours'], 2)

    def test_last_month_time_logged_duration(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(
            title="test title",
            description="test description",
            status="open")
        task.save()

        TimeLogFactory.create(
            start_time=datetime.now(),
            end_time=datetime.now(),
            task=task,
            duration=60)

        TimeLogFactory.create(
            start_time=datetime.now() - relativedelta(months=1),
            end_time=datetime.now(), task=task,
            duration=60
        )

        # act
        url = reverse('last_month_logged_time_duration')
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Total logged time in hours for last month'], 1)

    def test_tasks_list_duration(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        TimeLogFactory.create_batch(2, duration=60, task=task)

        task2 = TaskFactory.create()
        TimeLogFactory.create_batch(2, duration=120, task=task2)

        # act
        response = client.get('/api/tasks-list-duration/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['task_duration'], 120)
        self.assertEqual(response.data[1]['task_duration'], 240)

    def test_top_tasks_last_month(self):
        # arrange
        client = APIClient()
        task = TaskFactory.create()

        TimeLogFactory.create(
            start_time=datetime.now(),
            end_time=datetime.now(),
            task=task,
            duration=60)

        task2 = TaskFactory.create()
        two_months_ago = datetime.now() - relativedelta(months=2)
        TimeLogFactory.create(
            start_time=two_months_ago,
            end_time=two_months_ago,
            task=task2,
            duration=60)

        # act
        response = client.get('/api/top-tasks/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_tasks_list_details(self):
        # arrange
        client = APIClient()

        TaskFactory.create_batch(10)

        # act
        response = client.get('/api/tasks-list-details/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_tasks_list_details_filter_by_status(self):
        # arrange
        client = APIClient()
        tasks = TaskFactory.create_batch(2, status="open")

        tasks[1].status = "completed"
        tasks[1].save()

        # act
        response = client.get('/api/tasks-list-details/', {'status': 'completed'})

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_tasks_list_details_search(self):
        # arrange
        client = APIClient()

        tasks = TaskFactory.create_batch(2)
        tasks[1].title = "search title"
        tasks[1].save()

        # act
        response = client.get('/api/tasks-list-details/', {'search': 'search'})

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "search title")
