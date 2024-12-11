from django.db import models
from authors.models import Author
import uuid
from posts.models import Post

class Comment(models.Model):
    '''
    Represents the comments made on a post
    Comments can be made from local or remote authors
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    # post = models.URLField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comment_author')
    content = models.TextField(max_length=500)
    content_type = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    author_name = models.CharField(max_length=500)

    def __str__(self) -> str:
        return f"Comment by {self.author.display_name} on {self.post.title}"


class Like(models.Model):
    '''
    Represents a like action on a post or comment
    A like is created by an author and linked to the target object
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post')
    # post = models.URLField() #Url of the object being liked (eg. Post, Comment, etc.)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Like by {self.author.display_name} on {self.object}"
