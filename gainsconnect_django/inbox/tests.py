from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authors.models import Author
from posts.models import Post
from follow.models import Follower
import uuid

class InboxViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(
            uid=str(uuid.uuid4()),
            id=f'http://example.com/authors/{uuid.uuid4()}',
            displayName='Test Author'
        )

    def test_handle_post(self):
        post_uid = str(uuid.uuid4())
        post_data = {
            "type": "post",
            "id": f"http://example.com/api/authors/{self.author.uid}/posts/{post_uid}/",
            "title": "Test Post",
            "description": "A test post",
            "contentType": "text/plain",
            "content": "This is a test post content",
            "author": {
                "id": self.author.id,
                "displayName": self.author.displayName
            },
            "published": "2023-11-26T09:18:55.673794",
            "visibility": "public"
        }

        # Simulate a POST request
        response = self.client.post(
            f'/authors/{self.author.uid}/inbox',
            data=post_data,
            
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), "Post processed")

        # Check if the post was created
        self.assertTrue(Post.objects.filter(id=post_data['id']).exists())

    def test_handle_posts(self):
        post_uid_1 = str(uuid.uuid4())
        post_uid_2 = str(uuid.uuid4())
        posts_data = {
            "type": "posts",
            "items": [
                {
                    "type": "post",
                    "id": f"http://example.com/posts/{post_uid_1}",
                    "title": "Test Post 1",
                    "description": "A test post 1",
                    "contentType": "text/plain",
                    "content": "This is a test post content 1",
                    "author": {
                        "id": self.author.id,
                        "displayName": self.author.displayName
                    },
                    "published": "2023-11-26T09:18:55.673794",
                    "visibility": "public"
                },
                {
                    "type": "post",
                    "id": f"http://example.com/posts/{post_uid_2}",
                    "title": "Test Post 2",
                    "description": "A test post 2",
                    "contentType": "text/plain",
                    "content": "This is a test post content 2",
                    "author": {
                        "id": self.author.id,
                        "displayName": self.author.displayName
                    },
                    "published": "2023-11-26T09:18:55.673794",
                    "visibility": "public"
                }
            ]
        }

        # Simulate a POST request
        response = self.client.post(
            f'/authors/{self.author.uid}/inbox',
            data=posts_data,
            content_type='application/json'
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), "Posts processed")

        # Check if the posts were created
        self.assertTrue(Post.objects.filter(id=f"http://example.com/posts/{post_uid_1}").exists())
        self.assertTrue(Post.objects.filter(id=f"http://example.com/posts/{post_uid_2}").exists())