from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# Helper — shared login util
# ─────────────────────────────────────────────────────────────────────────────

def get_token(client, email, password):
    """Login and return the JWT access token string."""
    response = client.post(
        '/api/auth/login/',
        {'email': email, 'password': password},
        format='json',
    )
    return response.data['data']['access']


# ─────────────────────────────────────────────────────────────────────────────
# 1. Task Model Tests
# ─────────────────────────────────────────────────────────────────────────────

class TaskModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='modeluser',
            email='model@test.com',
            password='ModelPass123!',
        )
        self.task = Task.objects.create(
            user=self.user,
            title='Review X-ray',
            priority='high',
            status='todo',
            due_date='2026-07-10',
            tags=['radiology', 'urgent'],
        )

    # ── creation ─────────────────────────────────────────────────────────────
    def test_task_creation_stores_all_fields(self):
        self.assertEqual(self.task.title, 'Review X-ray')
        self.assertEqual(self.task.priority, 'high')
        self.assertEqual(self.task.status, 'todo')
        self.assertEqual(str(self.task.due_date), '2026-07-10')
        self.assertEqual(self.task.tags, ['radiology', 'urgent'])
        self.assertEqual(self.task.user, self.user)

    # ── default values ────────────────────────────────────────────────────────
    def test_task_default_priority_medium(self):
        task = Task.objects.create(
            user=self.user, title='Default Task', due_date='2026-07-10'
        )
        self.assertEqual(task.priority, 'medium')

    def test_task_default_status_todo(self):
        task = Task.objects.create(
            user=self.user, title='Default Task', due_date='2026-07-10'
        )
        self.assertEqual(task.status, 'todo')

    def test_task_default_order_zero(self):
        task = Task.objects.create(
            user=self.user, title='Default Task', due_date='2026-07-10'
        )
        self.assertEqual(task.order, 0)

    def test_task_default_tags_empty_list(self):
        task = Task.objects.create(
            user=self.user, title='Default Task', due_date='2026-07-10'
        )
        self.assertEqual(task.tags, [])

    # ── __str__ ───────────────────────────────────────────────────────────────
    def test_task_str_returns_title(self):
        self.assertEqual(str(self.task), 'Review X-ray')


# ─────────────────────────────────────────────────────────────────────────────
# 2. Task API Tests
# ─────────────────────────────────────────────────────────────────────────────

class TaskAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='ApiPass123!',
        )
        token = get_token(self.client, 'api@test.com', 'ApiPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ── CREATE ────────────────────────────────────────────────────────────────
    def test_create_task_returns_201(self):
        payload = {
            'title': 'Upload CT scan',
            'priority': 'high',
            'status': 'todo',
            'due_date': '2026-07-10',
            'tags': ['ct', 'scan'],
        }
        response = self.client.post('/api/tasks/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['title'], 'Upload CT scan')

    def test_create_task_saves_to_db(self):
        self.client.post('/api/tasks/', {
            'title': 'DB check task',
            'priority': 'low',
            'status': 'todo',
            'due_date': '2026-07-10',
        }, format='json')
        self.assertTrue(Task.objects.filter(title='DB check task').exists())

    def test_create_task_missing_title_returns_400(self):
        response = self.client.post('/api/tasks/', {
            'priority': 'low',
            'status': 'todo',
            'due_date': '2026-07-10',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    # ── LIST / FILTER BY DATE ─────────────────────────────────────────────────
    def test_list_tasks_returns_only_matching_date(self):
        Task.objects.create(user=self.user, title='Task A', due_date='2026-07-10', priority='low', status='todo')
        Task.objects.create(user=self.user, title='Task B', due_date='2026-07-11', priority='low', status='todo')

        response = self.client.get('/api/tasks/?date=2026-07-10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [t['title'] for t in response.data['data']]
        self.assertIn('Task A', titles)
        self.assertNotIn('Task B', titles)

    def test_list_tasks_without_date_returns_all_user_tasks(self):
        Task.objects.create(user=self.user, title='Task X', due_date='2026-07-10', priority='low', status='todo')
        Task.objects.create(user=self.user, title='Task Y', due_date='2026-07-11', priority='low', status='todo')

        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['data']), 2)

    def test_list_tasks_does_not_return_other_users_tasks(self):
        other = User.objects.create_user(
            username='otheruser', email='other@test.com', password='OtherPass123!'
        )
        Task.objects.create(user=other, title='Other Task', due_date='2026-07-10', priority='low', status='todo')

        response = self.client.get('/api/tasks/?date=2026-07-10')
        titles = [t['title'] for t in response.data['data']]
        self.assertNotIn('Other Task', titles)

    # ── UPDATE (PATCH) ────────────────────────────────────────────────────────
    def test_patch_task_updates_title_and_status(self):
        task = Task.objects.create(
            user=self.user, title='Old Title', due_date='2026-07-10',
            priority='low', status='todo',
        )
        response = self.client.patch(
            f'/api/tasks/{task.id}/',
            {'title': 'New Title', 'status': 'inprogress'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['title'], 'New Title')
        self.assertEqual(response.data['data']['status'], 'inprogress')

    def test_patch_task_partial_update_preserves_other_fields(self):
        task = Task.objects.create(
            user=self.user, title='Stable Title', due_date='2026-07-10',
            priority='high', status='todo',
        )
        self.client.patch(f'/api/tasks/{task.id}/', {'status': 'done'}, format='json')
        task.refresh_from_db()
        self.assertEqual(task.title, 'Stable Title')
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.status, 'done')

    def test_patch_other_users_task_returns_404(self):
        other = User.objects.create_user(
            username='patchother', email='patchother@test.com', password='OtherPass123!'
        )
        task = Task.objects.create(
            user=other, title="Other's Task", due_date='2026-07-10',
            priority='low', status='todo',
        )
        response = self.client.patch(f'/api/tasks/{task.id}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── DELETE ────────────────────────────────────────────────────────────────
    def test_delete_task_returns_200_and_removes_from_db(self):
        task = Task.objects.create(
            user=self.user, title='To Delete', due_date='2026-07-10',
            priority='low', status='todo',
        )
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_delete_other_users_task_returns_404(self):
        other = User.objects.create_user(
            username='delother', email='delother@test.com', password='OtherPass123!'
        )
        task = Task.objects.create(
            user=other, title="Other's Task", due_date='2026-07-10',
            priority='low', status='todo',
        )
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    # ── REORDER ───────────────────────────────────────────────────────────────
    def test_reorder_updates_status_and_order(self):
        task = Task.objects.create(
            user=self.user, title='Drag me', due_date='2026-07-10',
            priority='low', status='todo',
        )
        response = self.client.patch(
            f'/api/tasks/{task.id}/reorder/',
            {'status': 'done', 'order': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'done')
        self.assertEqual(task.order, 3)

    # ── AUTHENTICATION GUARD ──────────────────────────────────────────────────
    def test_unauthenticated_request_returns_401(self):
        self.client.credentials()
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)