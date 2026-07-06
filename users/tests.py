from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# Auth API Tests
# ─────────────────────────────────────────────────────────────────────────────

class AuthAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@test.com',
            password='LoginPass123!',
        )
        self.login_url = '/api/auth/login/'

    # ── LOGIN SUCCESS ─────────────────────────────────────────────────────────
    def test_login_with_correct_credentials_returns_200(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'LoginPass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_login_response_contains_access_and_refresh_tokens(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'LoginPass123!',
        }, format='json')
        data = response.data['data']
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertTrue(len(data['access']) > 10)
        self.assertTrue(len(data['refresh']) > 10)

    def test_login_response_contains_user_info(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'LoginPass123!',
        }, format='json')
        user_data = response.data['data']['user']
        self.assertEqual(user_data['email'], 'login@test.com')
        self.assertIn('id', user_data)
        self.assertIn('username', user_data)

    # ── LOGIN FAILURE ─────────────────────────────────────────────────────────
    def test_login_with_wrong_password_returns_401(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'WrongPassword!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_login_with_nonexistent_email_returns_401(self):
        response = self.client.post(self.login_url, {
            'email': 'nobody@test.com',
            'password': 'LoginPass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_login_with_wrong_password_does_not_return_token(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'WrongPassword!',
        }, format='json')
        self.assertNotIn('access', response.data)

    # ── ME ENDPOINT ───────────────────────────────────────────────────────────
    def test_me_returns_current_user_when_authenticated(self):
        login = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'LoginPass123!',
        }, format='json')
        token = login.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'login@test.com')

    def test_me_returns_401_when_unauthenticated(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── LOGOUT ────────────────────────────────────────────────────────────────
    def test_logout_with_valid_refresh_token_returns_200(self):
        login = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'LoginPass123!',
        }, format='json')
        access  = login.data['data']['access']
        refresh = login.data['data']['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        response = self.client.post('/api/auth/logout/', {'refresh': refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
