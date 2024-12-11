from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Author
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView

from .serializers import AuthorSerializer, RegisterSerializer, LoginSerializer, SimpleAuthorSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from .models import Author
from gainsconnect_django.settings import SERVER
from gainsconnect_django.views import parseURL
from node.views import NodeAuthentication
from node.models import Node
from urllib.parse import urlparse
from .swagger import swagger_docs
import requests
import base64


class AuthorView(APIView):
    authentication_classes = [NodeAuthentication]
    permission_classes = [IsAuthenticated]
    
    '''
    API view for handling author-related requests.
    
    - GET: Retrieves all authors in the database.
    - POST: Creates a new author using the provided data in the request body.
    '''
    def get(self, _):
        '''
        Retrieves all authors as a serialized list.

        ### `GET /authors/`
        - **Purpose**: Retrieves all authors in the database.
        - **When to Use**: When displaying a list of all authors.
        - **Why to Use**: Useful for managing author profiles or showing an author directory.

        #### Request
        - **Method**: GET

        #### Response
        - **Success**: 200 OK - Returns serialized author data as JSON.
        '''
        authors = Author.objects.exclude(is_remote = True).exclude(is_staff=True) #get all authors from db, excluding remote authors
        serializer = SimpleAuthorSerializer(authors, many=True) #serialize author data
        response = {
            "type": "authors",
            "authors": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK) #return serialized data as JSON
    
    def post(self, request):
        '''
        Creates a new author instance from the request data.

         ### `POST /authors/`
        - **Purpose**: Creates a new author instance from the request data.
        - **When to Use**: When registering a new author.
        - **Why to Use**: To add new authors to the platform.

        #### Request
        - **Method**: POST
        - **Body**:
        - Required author fields (e.g., "username", "email", "bio").

        #### Response
        - **Success**: 200 OK - Returns the newly created author data.
        - **Error**: 400 Bad Request - Returns validation errors.
        '''
        serializer = AuthorSerializer(data=request.data) #deserialize the incoming JSON data
        if serializer.is_valid():
            serializer.save() #save new author to db
            return Response(serializer.data, status=status.HTTP_200_OK) #return newly created author data
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #return error

#API view for registering users
class RegisterView(APIView):
    '''
    API view for handling user registration.
    '''
    permission_classes = [AllowAny]  # Allow anyone to access the signup endpoint
    authentication_classes = []  # Disable any JWT enforcement for this view

    def post(self, request):
        '''
        Registers a new user with the given credentials.

        ### `POST /api/signup/`
        - **Purpose**: Registers a new user with the given credentials.
        - **When to Use**: When a new user wants to sign up for an account.
        - **Why to Use**: To allow new users to join the platform.

        #### Request
        - **Method**: POST
        - **Body**:
        - "username" (string, required)
        - "email" (string, required)
        - "password" (string, required)

        #### Response
        - **Success**: 201 Created - Returns the user data on successful registration.
        - **Error**: 400 Bad Request - Returns validation errors.
        '''
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save the user to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API View for logging in users (Login)
class LoginView(APIView):
    '''
    API view for handling user login.
    '''
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        '''
        Authenticates the user with the provided credentials and returns JWT tokens.
        
        ### `POST /api/login/`
        - **Purpose**: Authenticates the user and returns JWT tokens.
        - **When to Use**: When a user logs in.
        - **Why to Use**: To allow users to securely access their accounts.

        #### Request
        - **Method**: POST
        - **Body**:
        - "username" (string, required)
        - "password" (string, required)

        #### Response
        - **Success**: 200 OK - Returns JWT tokens (access and refresh) upon successful authentication.
        - **Error**: 400 Bad Request - Returns validation errors.'''
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            #print the user id 
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    authentication_classes = [NodeAuthentication, JWTAuthentication]

    '''
    API view to retrieve an author's profile by ID.
    '''
    def get(self, _, id):
        '''
        Fetches the author profile based on the provided ID.

        ### `GET /profile/{id}/`
        - **Purpose**: Fetches the author profile based on the provided ID.
        - **When to Use**: When viewing an author's profile.
        - **Why to Use**: To display profile information of a specific author.

        #### Request
        - **Method**: GET
        - **URL Parameter**: `id` (integer, required) - The ID of the author.

        #### Response
        - **Success**: 200 OK - Returns serialized profile data.
        - **Error**: 404 Not Found - If the author does not exist.
        '''
        print("received request for profile information")
        # if recieved fqid
        if ('http' in id):
            print("received fqid")
            # if author is local
            if (SERVER in id):
                print("author is local")
                uid = parseURL(id)
                author = get_object_or_404(Author, uid=uid)
                serializer = AuthorSerializer(author)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print("author is remote")
                # parse url for host and remote uid
                parse = urlparse(id)
                host = f"{parse.scheme}://{parse.netloc}/"
                remote_uid = parseURL(id)
                host_node = get_object_or_404(Node, host=host)
                
                # fetch from remote node
                response = requests.get(f"{host_node.host}api/authors/{remote_uid}/", auth=(host_node.username, host_node.password))
                if response.status_code == 200:
                    serializer = SimpleAuthorSerializer(response.json())
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=response.status_code)

        # if received uuid
        else:
            print("received uuid")
            author = get_object_or_404(Author, uid=id)
            serializer = SimpleAuthorSerializer(author)
            return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    '''
    Handles profile updates (username, biography, profile picture, email, and GitHub username)
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("received request for profile update")
        print("Files:", request.FILES) 
        print("Data:", request.data)    
        
        user = request.user
        author = get_object_or_404(Author, username=user.username)

        # Update fields from the request data
        author.github = request.data.get('github_user', author.github)
        author.displayName = request.data.get('displayName', author.displayName)

        # Handle profile image if file was uploaded
        if 'profileImage' in request.FILES:
            print("profile image in request files")
            image_file = request.FILES['profileImage']
            print("image file", image_file)
            if image_file.size > 1024 * 1024 * 4:
                return Response({"error": "Profile image is too large. Maximum size is 4MB."}, 
                             status=status.HTTP_400_BAD_REQUEST)

            print("converting image to base64")
            # convert the image to base64 and save
            image = image_file.read()
            base64_str = base64.b64encode(image).decode('utf-8')
            author.profileImage = f"data:{image_file.content_type};base64,{base64_str}"

            print("converted image to base64")

        # if url was uploaded
        elif 'profileImage' in request.data:
            print("url image in request data")
            url = request.data['profileImage']
            if isinstance(url, str) and url.startswith('http'):
                author.profileImage = url

        author.save()
        print("saved author")
        serializer = AuthorSerializer(author)
        print("author after change", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(method='get', **swagger_docs["get_github_usernames"])
@api_view(['GET'])
def get_github_usernames(request):
    usernames = list(Author.objects.values_list('github', flat=True))
    return JsonResponse({'usernames': usernames})
class PaginatedAuthorsView(ListAPIView):
    """
    View to retrieve authors with pagination
    """
    #queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        host = self.request.query_params.get('host')
        if host:
            return Author.objects.filter(host=host)
        return Author.objects.all()
