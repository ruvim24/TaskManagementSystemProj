from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.tasks.models import Task


# Create your tests here.
class TaskTests(TestCase):
    def setUp(self) -> None:
        pass

    def test_task_get(self):
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()
        response = client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_list(self):
        client = APIClient()
        tasks_to_create = []
        for i in range(10):
            tasks_to_create.append(Task(title=f"test title {i}", description=f"test description {i}", status="open"))

        Task.objects.bulk_create(tasks_to_create)

        response = client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_task_create(self):
        client = APIClient()
        response = client.post('/api/tasks/',
                               {"title": "test title", "description": "test description", "status": "open"},
                               format='json')
        assert response.status_code == 201.
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["description"], "test description")
        self.assertEqual(response.data["status"], "open")

    def test_task_update(self):
        client = APIClient()
        task = Task.objects.create(title="some title", description="some description", status="open")
        task.save()

        update_data = {"title": "test title", "description": "test description", "status": "completed"}
        response = client.put(f'/api/tasks/{task.id}/', update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["description"], "test description")
        self.assertEqual(response.data["status"], "completed")

    def test_task_delete(self):
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        response = client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.filter(id=task.id).exists(), False)

    def test_task_complete(self):
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")

        response = client.put(f'/api/tasks/{task.id}/complete/')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).status, "completed")

    def test_task_comment(self):
        client = APIClient()
        task = Task.objects.create(title="test title", description="test description", status="open")
        task.save()

        response = client.post(f'api/tasks/{task.id}/comment/', {"comment": "test comment"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
