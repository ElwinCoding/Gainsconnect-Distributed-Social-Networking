from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from node.models import *
from authors.models import *
from follow.models import *
from posts.models import *
from gainsconnect_django.settings import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD

class NodeAPITest(APITestCase):
    def setUp(self):
        # create a client
        self.client1 = APIClient()
        self.client1.defaults['SERVER_NAME'] = 'localhost:8000'
        self.client1.defaults['HTTP_HOST'] = 'localhost:8000'

        # create a user
        signup_url = reverse("signup")
        test_user = {
            'display_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
        }
        self.client1.post(signup_url, test_user, format='json')

        # create a node
        self.node1 = Node.objects.create(
            name="Node 1", 
            host="http://localhost:8000/",
            username=BASIC_AUTH_USERNAME,
            password=BASIC_AUTH_PASSWORD,
            is_active=True,
            is_blocked=False
        )

    def test_missing_auth(self):
        '''
        Test that basic auth fails for unauthorized users 
        '''
        authors_url = reverse("getAuthors")
        self.client1.credentials()
        response = self.client1.get(authors_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_auth_failure(self):
        '''
        Test that basic auth fails for unauthorized users
        '''
        authors_url = reverse("getAuthors")
        credentials = base64.b64encode(b'wrong:wrong').decode('ascii')
        response = self.client1.get(authors_url, HTTP_AUTHORIZATION='Basic ' + credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_auth_success(self):
        '''Test that basic auth succeeds for authorized users'''
        authors_url = reverse("getAuthors")
        credentials = base64.b64encode(f'{self.node1.username}:{self.node1.password}'.encode()).decode('ascii')
        response = self.client1.get(authors_url, HTTP_AUTHORIZATION='Basic ' + credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)