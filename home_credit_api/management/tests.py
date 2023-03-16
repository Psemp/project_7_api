from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


from .models import Profile


class ProfileModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', email='test_user@example.com', password='testpass')
        self.profile = Profile.objects.create(user=self.user, is_staff=False)

    def test_str_representation(self):
        expected_str = f"{self.user.username} Profile"
        self.assertEqual(str(self.profile), expected_str)

    def test_profile_defaults(self):
        self.assertFalse(self.profile.is_staff)


class LogInTest(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'user_logintest',
            'email': 'email@mail.com',
            'password': 'Password1'}
        User.objects.create_user(**self.credentials)

    def test_login(self):

        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)


class RegisterTest(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'user_registertest',
            'email': 'email@mail.com',
            'password1': 'SuperSecretPassord12',
            'password2': 'SuperSecretPassord12'}

    def test_register_200(self):

        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register(self):

        self.client.post('/register/', self.credentials, follow=True)
        User.objects.get(username='user_registertest')


class ProfileTest(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'user_profiletest',
            'email': 'email@mail.com',
            'password': 'Password1'}
        User.objects.create_user(**self.credentials)


class TestLogout(TestCase):
    """Verifies the logout mechanic, dependant on login to be sucessful"""

    def setUp(self):
        self.credentials = {
            'username': 'user_logouttest',
            'email': 'email@mail.com',
            'password': 'Password1'}
        User.objects.create_user(**self.credentials)
        self.client.post('/login/', self.credentials, follow=True)  # Test user is logged in

    def test_logout(self):
        response = self.client.post('/logout/', self.credentials, follow=True)
        self.assertFalse(response.context['user'].is_active)
