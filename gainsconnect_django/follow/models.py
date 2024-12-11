from django.db import models
from authors.models import Author
from django.core.exceptions import ValidationError

class FollowRequest(models.Model):
    '''
    Represents a follow request sent by one author to another
    It stores the request status to indicate whether it is pending, accepted, or rejected
    '''
    type = models.CharField(default="follow", max_length=255)
    summary = models.CharField(max_length=255, default="")
    actor = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='sent_request')            # the one sending the request
    object = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='received_request')     # the one receiving the request
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('actor', 'object')

    def __str__(self) -> str:
        return f"{self.actor.displayName} sent {self.object.displayName} a follow request"
    
    

class Follower(models.Model):
    '''
    Represents a confirmed follower relationship between two authors
    Each record indicates that 'follower' is following 'target'
    '''
    follower = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='following') #author thats following another author
    followed = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followed') #author that is being followed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def clean(self):
        if self.follower == self.followed:
            raise ValidationError("Follower and followed cannot be the same.")

    def __str__(self) -> str:
        return f"{self.follower.displayName} follows {self.followed.displayName}"

class Friends(models.Model):
    '''
    Represents a friendship between two authors
    Each instance indicates that both authors are following each other
    '''
    author1 = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='friend1')
    author2 = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='friend2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('author1', 'author2')

    # store the relation in a consistent order to prevent duplicates
    def save(self, *args, **kwargs):
        if self.author1.id > self.author2.id:
            self.author1, self.author2 = self.author2, self.author1
        super().save(*args, **kwargs)