from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Post, Author
from django.contrib.auth.models import User
from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile

class StreamAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')  #replace with your actual signup URL name
        self.login_url = reverse('login')    #replace with your actual login URL name
        self.create_post_url = reverse('post-list-create')  #replace with the correct URL for post creation
        self.stream_url = reverse('stream')  #replace with the correct URL for the stream view

        self.test_user = {
            'display_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'profile_image': 'https://i.imgur.com/V4RclNb.png'
        }
        self.client.post(self.signup_url, self.test_user, format='json') #create a test user with signup API


    def test_create_post(self):

        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        #check that login and token return is succesful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        #retrieve author instance from db
        author = Author.objects.get(username=self.test_user['username'])
        #create new post
        post_data = {
            'author': str(author.id),
            'title': 'Test Post',
            'content': 'This is a Test Post.',
            'description': 'Testing the Post',
            'visibility': 'public',
        }
        response = self.client.post(self.create_post_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #check if the post exists in the database
        post_exists = Post.objects.filter(title='Test Post').exists()
        self.assertTrue(post_exists)

    def test_create_post_fail(self):

        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        #check that login and token return is succesful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        #retrieve author instance from db
        author = Author.objects.get(username=self.test_user['username'])
        
        #create new post, missing file
        post_data = {
            'author': str(author.id),
            'content': 'This is a Test Post.',
            'description': 'Testing the Post',
            'visibility': 'public',
        }
        response = self.client.post(self.create_post_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #check if the post exists in the database
        post_exists = Post.objects.filter(title='Test Post').exists()
        self.assertFalse(post_exists)

    def test_get_posts_on_stream(self):
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        #check that login and token return is succesful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        #check that login and token return is succesful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        #retrieve author instance from db
        author = Author.objects.get(username=self.test_user['username'])
        #create new post
        post_data = {
            'author': str(author.id),
            'title': 'Test Post',
            'content': 'This is a Test Post.',
            'description': 'Testing the Post',
            'visibility': 'public',
        }
        self.client.post(self.create_post_url, post_data, format='json')

        # Retrieve posts from the stream
        response = self.client.get(self.stream_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the post is in the response data
        self.assertTrue(any(post['title'] == 'Test Post' for post in response.data))
    def test_create_post_with_image(self):
        # Log in to get the token
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        # Check that login and token return is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        # Create a temporary image file
        image = io.BytesIO()
        image_file = Image.new('RGB', (100, 100), color='red')
        image_file.save(image, format='JPEG')
        image.seek(0)

        # Use SimpleUploadedFile to simulate an uploaded file
        uploaded_image = SimpleUploadedFile(
            "test_image.jpg",
            image.getvalue(),
            content_type="image/jpeg"
        )

        # Prepare the data for post creation, including the image
        author = Author.objects.get(username=self.test_user['username'])
        post_data = {
            'author': str(author.id),
            'title': 'Test Post with Image',
            'content': 'This is a test post with an image.',
            'description': 'Testing image upload.',
            'visibility': 'public',
            'image': uploaded_image  # Include the image file as a SimpleUploadedFile
        }

        # Make a POST request to create a post with an image
        response = self.client.post(self.create_post_url, post_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the post with the image exists in the database
        post = Post.objects.filter(title='Test Post with Image').first()
        self.assertIsNotNone(post)
        self.assertIsNotNone(post.image)  # Check if the image field is populated

    def test_create_post_with_commonmark(self):
        # Log in to get the token
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        # Check that login and token return is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        # Markdown content for the post
        markdown_content = "**Bold Text** and *Italic Text*."

        # Retrieve author instance from the database
        author = Author.objects.get(username=self.test_user['username'])

        # Create post data with Markdown content
        post_data = {
            'author': str(author.id),
            'title': 'Test Post with Markdown',
            'content': markdown_content,
            'content_type': 'text/markdown',
            'description': 'Testing raw Markdown content storage.',
            'visibility': 'public',
        }

        # Make a POST request to create the post
        response = self.client.post(self.create_post_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the post data from the API
        post_id = response.data['id']  # Assuming the response contains the post ID
        post_detail_url = reverse('post-detail', args=[post_id])
        response = self.client.get(post_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the backend stored the raw Markdown content
        stored_content = response.data['content']
        self.assertEqual(stored_content, markdown_content)

    def test_delete_post(self):
        # Log in to get the token
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')

        # Check that login and token return is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        # Create a post that will be deleted
        author = Author.objects.get(username=self.test_user['username'])
        post_data = {
            'author': str(author.id),
            'title': 'Post to be Deleted',
            'content': 'This post will be deleted.',
            'description': 'Testing post deletion from stream.',
            'visibility': 'public',
        }

        # Make a POST request to create the post
        create_response = self.client.post(self.create_post_url, post_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Get the ID of the newly created post
        post_id = create_response.data['id']  # Ensure this ID is correct
        delete_url = reverse('delete_post', args=[post_id])

        # Make a DELETE request to delete the post
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the post no longer appears in the stream view
        stream_response = self.client.get(self.stream_url, format='json')
        self.assertEqual(stream_response.status_code, status.HTTP_200_OK)

        # Ensure the post is not in the stream data
        self.assertFalse(any(post['id'] == post_id for post in stream_response.data))

        # Check that the post still exists in the database
        post_exists = Post.objects.filter(id=post_id).exists()
        self.assertTrue(post_exists)  # This should pass since the post should still be in the database


