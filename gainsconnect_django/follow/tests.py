from django.urls import reverse
from .models import *
from rest_framework.test import APITestCase
from rest_framework import status

class FollowRequestAPITest(APITestCase): 
    
    def setUp(self):
        signup_url = reverse("signup")
        login_url = reverse("login")

        # create 2 authors
        test_user = {
            'display_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
        }
        self.client.post(signup_url, test_user, format='json') #create a test user with signup API

        test_user2 = {
            'display_name': 'Tester',
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'password123',
        }
        self.client.post(signup_url, test_user2, format='json') #create a test user with signup API

        login_data = {
            'username': test_user['username'],
            'password': test_user['password']
        }

        login_data2 = {
            'username': test_user2['username'],
            'password': test_user2['password']
        }

        # obtain the user id or author1
        response = self.client.post(login_url, login_data, format='json')
        self.user1ID = str(response.data['id'])
        
        # obtain the user id or author2
        response = self.client.post(login_url, login_data2, format='json')
        self.user2ID = str(response.data['id'])

    def test_explore_api(self):
        explore_url = reverse("exploreAuthors", kwargs={'id': self.user1ID})
        response = self.client.get(explore_url)
        
        # check that explore is showing other author(s)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_send_receive_request(self):
        send_request_url = reverse("followRequest")
        request_data = {
            'sender': self.user1ID,
            'receiver': self.user2ID
        }
        # send a follow request from user1 to user2
        response = self.client.post(send_request_url, request_data, format='json')

        # check request is sent
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test if request is received
        receive_request_url = reverse("receiveList", kwargs={'id': self.user2ID})
        response = self.client.get(receive_request_url)
        
        # check request has been received
        self.assertTrue(len(response.data) > 0)


class FollowAPITest(APITestCase): 

    def setUp(self):
        signup_url = reverse("signup")
        login_url = reverse("login")

        # create 2 authors
        test_user = {
            'display_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
        }
        self.client.post(signup_url, test_user, format='json') #create a test user with signup API

        test_user2 = {
            'display_name': 'Tester',
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'password123',
        }
        self.client.post(signup_url, test_user2, format='json') #create a test user with signup API

        login_data = {
            'username': test_user['username'],
            'password': test_user['password']
        }

        login_data2 = {
            'username': test_user2['username'],
            'password': test_user2['password']
        }

        # obtain the user id or author1
        response = self.client.post(login_url, login_data, format='json')
        self.user1ID = str(response.data['id'])
        
        # obtain the user id or author2
        response = self.client.post(login_url, login_data2, format='json')
        self.user2ID = str(response.data['id'])

        # send a request from user1 to user2
        self.send_request_url = reverse("followRequest")
        request_data = {
            'sender': self.user1ID,
            'receiver': self.user2ID
        }
        self.client.post(self.send_request_url, request_data, format='json')

    def test_decline_request(self):
        # decline follow request
        decline_request_url = reverse('handleRequest')
        decline_request_data = {
            'sender': self.user1ID,
            'receiver': self.user2ID,
            'reply': False
        }
        response = self.client.post(decline_request_url, decline_request_data, format='json')
        # check if success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accept_request(self):
        # accept follow request
        accept_request_url = reverse('handleRequest')
        accept_request_data = {
            'sender': self.user1ID,
            'receiver': self.user2ID,
            'reply': True
        }
        response = self.client.post(accept_request_url, accept_request_data, format='json')
        
        # check if success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if user1 is a follower of user2
        followed_url = reverse('getList', kwargs={'id': self.user2ID, 'category': 'followed'})
        response = self.client.get(followed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        # check if user1 is following user2
        following_url = reverse('getList', kwargs={'id': self.user1ID, 'category': 'following'})        
        response2 = self.client.get(following_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response2.data) > 0)

    def test_friends(self):
        # accept follow request on user2
        accept_request_url = reverse('handleRequest')
        accept_request_data = {
            'sender': self.user1ID,
            'receiver': self.user2ID,
            'reply': True
        }
        self.client.post(accept_request_url, accept_request_data, format='json')
        
        # send request from user2 to user1
        request_data2 = {
            'sender': self.user2ID,
            'receiver': self.user1ID
        }
        self.client.post(self.send_request_url, request_data2, format='json')
        
        # accept follow request on user1
        accept_request_data2 = {
            'sender': self.user2ID,
            'receiver': self.user1ID,
            'reply': True
        }
        self.client.post(accept_request_url, accept_request_data2, format='json')
        
        # check if user1 and user2 are friends
        friends_url = reverse('getList', kwargs={'id': self.user1ID, 'category': 'friends'})
        response = self.client.get(friends_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_unfollow(self):
        # accept follow request from user1 on user2
        accept_request_url = reverse('handleRequest')
        accept_request_data = {
            'sender': self.user1ID,
            'receiver': self.user2ID,
            'reply': True
        }
        self.client.post(accept_request_url, accept_request_data, format='json')
        
        # unfollow user2 from user1
        unfollow_url = reverse('unfollow')
        unfollow_data = {
            'user': self.user1ID,
            'author': self.user2ID
        }
        response = self.client.post(unfollow_url, unfollow_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)