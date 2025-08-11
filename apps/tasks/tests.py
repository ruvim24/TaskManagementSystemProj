from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.tasks.models import Task, Comment, TimeLog


# Create your tests here.
class TaskTests(TestCase):
    def setUp(self) -> None:
        pass

    def test_task_get(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        # act
        response = client.get(f'/api/tasks/{task.id}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_list(self):
        # arrange
        client = APIClient()
        tasks_to_create = []
        for i in range(10):
            tasks_to_create.append(Task(title=f"test title {i}", description=f"test description {i}", status="open"))
        Task.objects.bulk_create(tasks_to_create)

        # act
        url = reverse('tasks-list')
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_task_create(self):
        # arrange
        client = APIClient()

        # url = reverse('tasks-create')
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
        task = Task.objects.create(title="some title", description="some description", status="open")
        task.save()
        update_data = {"title": "test title", "description": "test description", "status": "completed"}

        # act
        # url = reverse('tasks-update', kwargs={'pk': task.id})
        response = client.put(f'/api/tasks/{task.id}/', update_data, format='json')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["description"], "test description")
        self.assertEqual(response.data["status"], "completed")

    def test_task_delete(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        # act
        # url = reverse('tasks-destroy', kwargs={'pk': task.id})

        response = client.delete(f'/api/tasks/{task.id}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.filter(id=task.id).exists(), False)

    def test_task_complete(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")

        # act
        # url = reverse('tasks-complete', kwargs={'task_id': task.id})
        response = client.put(f'/api/tasks/{task.id}/complete/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).status, "completed")

    def test_task_create_comment(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

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
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()
        comments_to_create = []
        for i in range(10):
            comments_to_create.append(Comment(content=f"test comment {i}", task=task))
        Comment.objects.bulk_create(comments_to_create)

        # act
        response = client.get(f'/api/tasks/{task.id}/comments/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_start_timer_should_be_successfully(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        # act
        response = client.post(f'/api/tasks/{task.id}/start-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_start_timer_should_fail(self):
        # arange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="completed")
        task.save()
        TimeLog.objects.create(task=task, start_time=datetime.now())

        # act
        response = client.post(f'/api/tasks/{task.id}/start-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stop_timer_should_fail(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        # act
        response = client.put(f'/api/tasks/{task.id}/stop-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stop_timer_should_be_successfully(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="completed")
        task.save()
        TimeLog.objects.create(task=task, start_time=datetime.now())

        # act
        response = client.put(f'/api/tasks/{task.id}/stop-timer/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_get_time_logs_should_be_successfully(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()
        time_logs_to_create = []
        for i in range(10):
            time_logs_to_create.append(TimeLog(start_time=datetime.now(), end_time=datetime.now(), task=task))

        TimeLog.objects.bulk_create(time_logs_to_create)

        # act
        response = client.get(f'/api/tasks/{task.id}/time-logs/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_log_time_should_be_successfully(self):
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

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
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        time_logs = []
        for i in range(2):
            time_logs.append(TimeLog(start_time=datetime.now(), end_time=datetime.now(), task=task, duration=60))
        TimeLog.objects.bulk_create(time_logs)

        # act
        response = client.get(f'/api/tasks/{task.id}/logged-time-duration/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Total logged time in hours'], 2)

    def test_last_month_time_logged_duration(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        TimeLog.objects.create(start_time=datetime.now(), end_time=datetime.now(), task=task, duration=60)
        TimeLog.objects.create(
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
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        time_logs = []
        for i in range(2):
            time_logs.append(TimeLog(start_time=datetime.now(), end_time=datetime.now(), task=task, duration=60))

        TimeLog.objects.bulk_create(time_logs)

        task2 = Task.objects.create(title="test title2", description="test description2", status="open")
        task2.save()
        time_logs2 = []
        for i in range(2):
            time_logs2.append(TimeLog(start_time=datetime.now(), end_time=datetime.now(), task=task2, duration=120))
        TimeLog.objects.bulk_create(time_logs2)

        # act
        response = client.get('/api/tasks/duration/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['task_duration'], 120)
        self.assertEqual(response.data[1]['task_duration'], 240)

    def test_top_tasks_last_month(self):
        # arrange
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        time_log = TimeLog.objects.create(start_time=datetime.now(), end_time=datetime.now(), task=task,
                                          duration=60)
        time_log.save()

        task2 = Task.objects.create(title="test title2", description="test description2", status="open")
        task2.save()
        two_months_ago = datetime.now() - relativedelta(months=2)

        time_log2 = TimeLog.objects.create(start_time=two_months_ago, end_time=two_months_ago, task=task2,
                                           duration=60)
        time_log2.save()

        # act
        response = client.get('/api/tasks/top-tasks/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_tasks_list_details(self):
        # arrange
        client = APIClient()

        tasks_to_create = []
        for i in range(10):
            tasks_to_create.append(
                Task(title=f"test title {i}", description=f"test description {i}", status="open"))

        Task.objects.bulk_create(tasks_to_create)

        # act
        response = client.get('/api/tasks/list/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(tasks_to_create))

    def test_tasks_list_details_filter_by_status(self):
        # arrange
        client = APIClient()
        tasks_to_create = []
        for i in range(2):
            tasks_to_create.append(
                Task(title=f"test title {i}", description=f"test description {i}", status="open"))
        tasks_to_create[1].status = "completed"
        Task.objects.bulk_create(tasks_to_create)

        # act
        response = client.get('/api/tasks/list/', {'status': 'completed'})

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_tasks_list_details_search(self):
        # arrange
        client = APIClient()
        tasks_to_create = []
        for i in range(2):
            tasks_to_create.append(
                Task(title=f"test title {i}", description=f"test description {i}", status="open"))
        tasks_to_create[1].title = "search title"
        Task.objects.bulk_create(tasks_to_create)

        # act
        response = client.get('/api/tasks/list/', {'search': 'search'})

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "search title")
