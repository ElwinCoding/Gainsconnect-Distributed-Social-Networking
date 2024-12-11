from django.test import TestCase

from rest_framework.test import APITestCase
from django.urls import reverse
from posts.models import Post
from .models import Comment
from django.contrib.auth.models import User
from rest_framework import status
from .models import Like
import uuid
from .models import Author


class AddCommentApiTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(title='Test Post', content='This is a test post.')
        self.url = reverse('add_comment_api', args=[self.post.id])
        self.client.login(username='testuser', password='testpass')

    def test_add_comment_api_valid(self):
        data = {
            'content': 'Test comment via API'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(content='Test comment via API', post=self.post).exists())

    def test_add_comment_api_invalid_json(self):
        response = self.client.post(self.url, 'Invalid JSON', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_add_comment_api_invalid_data(self):
        data = {
            'content': ''  # Empty content
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

class GetCommentsApiTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(title='Test Post', content='This is a test post.')
        Comment.objects.create(post=self.post, author=self.user, content='Test comment 1')
        Comment.objects.create(post=self.post, author=self.user, content='Test comment 2')
        self.url = reverse('get_comments_api', args=[self.post.id])

    def test_get_comments_api(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # There should be 2 comments

class AddLikeApiTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_add_like_api(self):
        data = {
            'object': 'http://example.com/posts/1',
        }
        response = self.client.post(reverse('add_like_api'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(object='http://example.com/posts/1').exists())
class GetLikeCountApiTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(title='Test Post', content='This is a test post.')
        Like.objects.create(author=self.user, object=f'http://example.com/posts/{self.post.id}')
        self.url = reverse('get_like_count_api', args=[self.post.id])

    def test_get_like_count_api(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 1)

class APITestCaseForViews(APITestCase):
    def setUp(self):
        # Create a sample author
        self.author = Author.objects.create(
            uid=str(uuid.uuid4()),
            username="test_author",
            displayName="Test Author",
            github="http://github.com/testauthor",
            profileImage="http://example.com/profile.jpg",
        )
        
        # Create another author
        self.other_author = Author.objects.create(
            uid=str(uuid.uuid4()),
            username="other_author",
            displayName="Other Author",
            github="http://github.com/otherauthor",
            profileImage="http://example.com/otherprofile.jpg",
        )

        # Create a post
        self.post = Post.objects.create(
            uid=str(uuid.uuid4()),
            author=self.author,
            title="Test Post",
            content="This is a test post."
        )

        # Create a comment
        self.comment = Comment.objects.create(
            id=str(uuid.uuid4()),
            post=self.post,
            author=self.other_author,
            content="This is a test comment.",
            content_type="text/plain"
        )

        # Create a like
        self.like = Like.objects.create(
            id=str(uuid.uuid4()),
            post=self.post,
            author=self.other_author
        )

        self.client = APIClient()

    def test_author_post_likes_view(self):
        url = reverse('authorPostLikesView', args=[self.author.uid, self.post.uid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['type'], 'likes')

    def test_author_post_comment_likes_view(self):
        url = reverse('authorPostCommentLikesView', args=[self.author.uid, self.post.uid, self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['type'], 'likes')

    def test_all_liked_uid_view(self):
        url = reverse('allLikedUIDView', args=[self.other_author.uid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['type'], 'likes')

    def test_liked_view(self):
        url = reverse('likedView', args=[self.other_author.uid, self.like.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'like')

    def test_get_comments_by_post_id_view(self):
        url = reverse('getCommentsByPostIDView', args=[self.author.uid, self.post.uid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['type'], 'comments')

    def test_get_comments_by_post_fqid_view(self):
        url = reverse('getCommentsByPostFQIDView', args=[f"http://nodebbbb/api/posts/{self.post.uid}"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['type'], 'comments')

    def test_get_comment_by_fqid_view(self):
        url = reverse('getCommentByFQIDView', args=[self.author.uid, self.post.uid, self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comment')

    def test_get_all_comments_by_author_uid_view(self):
        url = reverse('getAllCommentsByAuthorByUIDView', args=[self.other_author.uid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['type'], 'comments')

    def test_get_commented_comment_by_uid_view(self):
        url = reverse('getCommentedCommentByUIDView', args=[self.other_author.uid, self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comment')
