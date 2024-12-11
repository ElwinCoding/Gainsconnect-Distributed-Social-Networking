from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from gainsconnect_django.settings import SERVER
import uuid
from gainsconnect_django.views import parseURL

class AuthorManager(BaseUserManager):
    '''
    Custom manager for Author model where email and password is mandatory
    '''

    #create instance of general user with email, username, and password all mandatory
    def create_user(self, username, email, password, **extrafields):
        if not email:
            raise ValueError('The email field must be filled')
        if not username:
            raise ValueError('The username field must be filled')
        if not password:
            raise ValueError('The password field must be filled')
        
        email = self.normalize_email(email) #normalize email by lowercasing the domain part
        user = self.model(username=username, email=email, **extrafields) #new instance of Author model with provided fields
        user.set_password(password) #hash and set the password
        user.save(using=self._db) #save user instance in db
        return user
    

    def create_superuser(self, username, email, password=None, **extrafields):
        if not password:
            raise ValueError('The password field must be filled')

        #setting flags for superusers to True
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_superuser', True)
        extrafields.setdefault('is_active', True)

        if extrafields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff set to True')
        if extrafields.get('is_superuser') is not True:
            raise ValueError('Super user must have is_superuser set to True')
        
        #create and return new superuser using create_user method
        return self.create_user(username, email, password, **extrafields)
    
    def create_remote_author(self, remote_data):
        remote_uid = parseURL(remote_data.get('id'))
        
        # validate received uid, else create one
        try:
            uid = uuid.UUID(remote_uid)
        except ValueError:
            uid = uuid.uuid4()

        author = self.model(
            uid = uid, 
            is_remote = True,
            id = remote_data.get('id'),
            displayName = remote_data.get('displayName'),
            profileImage = remote_data.get('profileImage', 'https://i.imgur.com/V4RclNb.png'),
            host = remote_data.get('host'),
            github = remote_data.get('github'),
            page = remote_data.get('page'),
            username = remote_data.get('host') + remote_data.get('displayName') + str(uid),
            email = str(uid) + "@remote.com",
        )
        author.set_unusable_password()
        author.save()
        return author
    

class Author(AbstractBaseUser, PermissionsMixin):
    '''
    Represents a user on the distributed social network
    Inherits from AbstractBaseUser and PermissionMixin to provide core fields and functionality for user authentication
    '''
    type = models.CharField(max_length=30, default='author', editable=False)

    #UUIDs are 128 bit values, used to uniquely identify objects
    #uuid.uuid4 is to automatically assign a unique id once a new record is created
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True) #unique identifier universally
    id = models.URLField(max_length=200, blank=True, null=True)
    
    #username used as unique identifier for authentication instead of default email
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)

    #email field must be unique across all users
    email = models.EmailField(unique=True, null=True, blank=True)

    displayName = models.CharField(max_length=30)
    profileImage = models.TextField(max_length=2000, blank=True, default='https://i.imgur.com/V4RclNb.png')
    host = models.URLField(max_length=500, default=SERVER + 'api/', blank=True) #the url of the server where the author is hosted
    page = models.TextField(max_length=200, blank=False, editable=False)
    biography = models.TextField(blank=True, null=True)
    github = models.CharField(max_length=255, blank=True, null=True)

    #fields required for Django user model for handling user state and permissions
    is_active = models.BooleanField(default=True)  # change to False to require approval
    is_staff = models.BooleanField(default=False)

    # to indicate if author is remote or local
    is_remote = models.BooleanField(default=False)

    joined = models.DateTimeField(default=timezone.now)

    objects = AuthorManager() #custom manager to be used for Author model

    USERNAME_FIELD = 'username' #unique identifier for authentication
    REQUIRED_FIELDS = ['email'] #list of fields required for creating superuser

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.username or self.displayName or self.email or 'Unnamed Author'

    