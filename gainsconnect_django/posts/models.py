import uuid
from django.db import models
from authors.models import Author
from django.urls import reverse
from gainsconnect_django.settings import SERVER
import base64
from django.core.files.base import ContentFile

class Post(models.Model):
    '''
    Represents a post created by an Author
    A post can be shared across nodes and may contain text, images, or other content types
    '''
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'PUBLIC'),      
        ('FRIENDS', 'FRIENDS'),    
        ('UNLISTED', 'UNLISTED'),
        ('DELETED', 'DELETED'),  
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base64'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    ]

    type = models.CharField(max_length=30, default='post', editable=False)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.URLField(max_length=200, blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    content = models.TextField() # description of post
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/plain') #content type of post eg.(text/plain)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='PUBLIC')  # to keep track if it is public, unlisted, friends-only
    published = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) #keep track of most recently edited posts
    is_deleted = models.BooleanField(default=False)
    comments = models.IntegerField(default=0) # count of how many comment objects are associated with the post
    likes = models.IntegerField(default = 0) #url to access the likes of the post
    #original_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reposts')
    #image = models.ImageField(upload_to='post_images/', null=True, blank=True) #Image for the post


    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{SERVER}api/authors/{self.author.uid}/posts/{self.uid}"
        
        if self.contentType == 'image/png;base64' or self.contentType == 'image/jpeg;base64':
            try:
                # Remove the data URI header if present
                if 'data:' in self.content and ';base64,' in self.content:
                    header, base64_data = self.content.split(';base64,')
                else:
                    base64_data = self.content

                # store base64 data in content field
                self.content = base64_data
            
            except Exception as e:
                print(f"Error processing base64 image: {e}")
        super().save(*args, **kwargs)

    def get_content(self):
        """Returns the content in appropriate format"""
        if self.contentType in ['image/png;base64', 'image/jpeg;base64']:
            # Return with proper data URI prefix for images
            mime_type = 'image/png' if self.contentType == 'image/png;base64' else 'image/jpeg'
            return f"data:{mime_type};base64,{self.content}"
        return self.content

    @property
    def content_is_image(self):
        """Check if the content is an image"""
        return self.contentType in ['image/png;base64', 'image/jpeg;base64']


    def __str__(self) -> str:
        return self.title