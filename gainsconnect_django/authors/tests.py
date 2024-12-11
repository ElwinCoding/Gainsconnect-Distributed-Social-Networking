from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Author
from rest_framework_simplejwt.tokens import RefreshToken

class AuthenticationAPITestClass(APITestCase):
    def setUp(self):
        self.signup_url = reverse("signup")
        self.login_url = reverse("login")
        self.test_user = {
            'display_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'profile_image': 'https://i.imgur.com/V4RclNb.png'
        }
        self.client.post(self.signup_url, self.test_user, format='json') #create a test user with signup API

    def test_signup_success(self):
        signup_data = {
            'display_name': 'new User',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'profile_image': 'https://i.imgur.com/V4RclNb.png'
        }
        response = self.client.post(self.signup_url, signup_data, format='json')

        #check if user was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], signup_data['email'])

    def test_signup_empty_fields(self):
        signup_data = {
            'email': 'incomplete@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.signup_url, signup_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        #check that login and token return is succesful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        invalid_login_data = {
            'username': 'dne',
            'password': 'dne'
        }
        response = self.client.post(self.login_url, invalid_login_data, format='json')
        
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) #400 instead of 401?
        #DRF always treats ValidationError as a 400 Bad Request by default. This is why test is failing even though we manually set code='authorization' in the serializer
        #should be consistent with other nodes as they are using DRF
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_password(self):
        no_password_login = {
            'username': self.test_user['username']
        }
        response = self.client.post(self.login_url, no_password_login, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from rest_framework.test import APIClient

class AuthorGitHubAPITests(TestCase):
    def setUp(self):
        # Set up the test data (Authors with GitHub usernames)
        self.client = APIClient()
        self.author1 = Author.objects.create(
            username='author1',
            github_username='author1_github',
            email='author1@example.com',  # Provide a unique email
        )
        self.author2 = Author.objects.create(
            username='author2',
            github_username='author2_github',
            email='author2@example.com',  # Provide a different unique email
        )
    
    def test_github_usernames_endpoint(self):
        # Hit the endpoint and fetch the response
        response = self.client.get(reverse('github_usernames'))
        
        # Check if the status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the returned data contains only the GitHub usernames
        expected_data = {
            'usernames': ['author1_github', 'author2_github']
        }
        
        # Assert that the response matches the expected data
        self.assertEqual(response.json(), expected_data)


