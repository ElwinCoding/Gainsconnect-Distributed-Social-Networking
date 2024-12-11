from django.shortcuts import get_object_or_404, redirect, render
from .models import Comment
from posts.models import Post
from authors.models import Author
from .forms import CommentForm
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CommentSerializer
from rest_framework import generics
from .models import Like
from .serializers import LikeSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from django.urls import reverse
import requests
from authors.serializers import SimpleAuthorSerializer
from urllib.parse import urlparse
from node.models import Node
from gainsconnect_django.settings import SERVER 
from follow.models import Follower





#for handling comments from html forms only
#may be useful for debugging until frontend ui is set up
# API endpoint for adding a comment to a post

def add_comment(request, post_id):
    '''
    Handles adding comments via HTML forms for debugging purposes.
    
    ### `GET /comments/{post_id}/add/`
    - **Purpose**: Display a form to add a comment.
    - **When to Use**: Primarily for backend debugging before UI is implemented.
    - **Why to Use**: Useful for testing comment functionality.

    #### Request
    - **Method**: GET or POST
    - **URL Parameter**: `post_id` (string, required) - ID of the post to comment on.

    #### Response
    - **Success**: Redirects to the post detail page after saving the comment.
    '''
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    
    
    return render(request, 'add_comment.html', {'form': form})

#api endpoint for handling incoming post comment requests from vue
# API endpoint for adding a comment to a post
@swagger_auto_schema(
    method='post',
    operation_summary="Add a comment to a post",
    operation_description="Endpoint for adding a comment to the specified post.",
    request_body=CommentSerializer,
    responses={
        201: openapi.Response(
            description="Created",
            examples={"application/json": {"id": 1, "content": "Example comment content", "author": 1}}
        ),
        400: openapi.Response(description="Validation errors")
    }
)
@api_view(['POST'])
def add_comment_api(request, post_uid):
    """
    API endpoint to add a comment to a post and send it to the appropriate node inboxes or followers.
    """
    post = get_object_or_404(Post, uid=post_uid)

    if request.content_type != 'application/json':
        return Response({'detail': 'Content-Type must be application/json'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data.copy()
    data['author'] = request.user.uid
    author = get_object_or_404(Author, id=request.user.id)
    data['author_name'] = author.displayName

    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        comment = serializer.save(
            post=post,
            author=author,
            content_type=data["content_type"],
            content=data["content"],
            author_name=author.displayName,
        )
        post.comments += 1
        post.save()

        # Prepare the comment object for the inbox
        comment_data = {
            "type": "comment",
            "author": SimpleAuthorSerializer(request.user).data,
            "comment": comment.content,
            "contentType": comment.content_type,
            "published": comment.created_at.isoformat(),
            "id": f"{request.build_absolute_uri()}/comments/{comment.id}",
            "post": post.id,
        }

        print("COMMENT OBJECT:", comment_data)

        if SERVER in post.author.id:
            # If the post is local, send the comment to the followers of the author
            print("Post is local")
            followers = Follower.objects.filter(followed=request.user)
            print ("FOLLOWERS:", followers)
            for follower in followers:
                try:
                    # Prepare inbox URL
                    follower_url = urlparse(follower.follower.id)
                    base_url = f"{follower_url.scheme}://{follower_url.netloc}/"
                    inbox_url = f"{follower.follower.id}/inbox"
                    print ("FOLLOWER: ", follower)
                    print("INBOX URL:", inbox_url)

                    # Retrieve the host node
                    host_node = Node.objects.get(host=base_url)
                    if not host_node.is_active or host_node.is_blocked:
                        print(f"Node for host {base_url} is not active.")
                        continue

                    print ("HOST", host_node)       
                    # Send the comment to the follower's inbox
                    response = requests.post(
                        inbox_url,
                        json=comment_data,
                        auth=(host_node.username, host_node.password),
                        headers={'Content-Type': 'application/json'},
                    )

                    print(f"Response for follower {follower.follower.displayName}: {response.status_code}")
                    if not (200 <= response.status_code < 300):
                        print(f"Failed to send comment to follower {follower.follower.displayName}: {response.content}")

                except Exception as e:
                    print(f"Error sending comment to follower {follower.follower.displayName}: {e}")

        else:
            # If the post is remote, send the comment back to the parent node
            print("Post is remote")
            try:
                # Parse the author's ID to get the base URL
                author_url = urlparse(post.author.id)
                base_url = f"{author_url.scheme}://{author_url.netloc}/"
                inbox_url = f"{post.author.id}/inbox"

                # Retrieve the host node
                host_node = Node.objects.get(host=base_url)
                if not host_node.is_active or host_node.is_blocked:
                    print(f"Node for host {base_url} is not active.")
                    return Response("Node for host {base_url} is not active", status=status.HTTP_400_BAD_REQUEST)

                print("HOST NODE:", host_node)
                print("INBOX URL:", inbox_url)
                print("COMMENT DATA:", comment_data)

                # Send the comment to the parent node's inbox
                response = requests.post(
                    inbox_url,
                    json=comment_data,
                    auth=(host_node.username, host_node.password),
                    headers={'Content-Type': 'application/json'},
                )
                print(f"Response from parent node: {response.status_code}")
                if not (200 <= response.status_code < 300):
                    print(f"Failed to send comment to parent node: {response.content}")

            except Exception as e:
                print(f"Error sending comment to parent node: {e}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#get comments by post id
# API endpoint to get all comments for a specific post
@swagger_auto_schema(
    method='get',
    operation_summary="Get comments for a post",
    operation_description="Retrieve all comments associated with the specified post.",
    responses={
        200: openapi.Response(
            description="Success",
            examples={"application/json": [{"id": 1, "content": "Example comment", "author": 1}]}
        ),
    }
)
@api_view(['GET'])
def get_comments_api(request, post_uid):
    '''
    API endpoint to retrieve all comments for a specific post.

    ### `GET /api/posts/{post_id}/comments/`
    - **Purpose**: Retrieves comments for the specified post.
    - **When to Use**: When displaying all comments for a post.
    - **Why to Use**: Provides users with the ability to view discussion on a post.

    #### Request
    - **Method**: GET
    - **URL Parameter**: `post_id` (string, required) - ID of the post.

    #### Response
    - **Success**: 200 OK - Returns a list of comments sorted by creation time.
    '''

    # Retrieve the post or return a 404 if not found
    post = get_object_or_404(Post, uid=post_uid)
    
    # Filter comments related to the post and order them by creation time
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    
    # Serialize the list of comments
    serializer = CommentSerializer(comments, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


#api endpoint for handling incoming post like requests from vue
@swagger_auto_schema(
    method='post',
    operation_summary="Add a like to a post",
    operation_description="Endpoint to add a like to the specified post.",
    request_body=LikeSerializer,
    responses={
        201: openapi.Response(
            description="Created",
            examples={"application/json": {"id": 1, "author": 1}}
        ),
        400: openapi.Response(description="Validation errors")
    }
)
@api_view(['POST'])
def add_like_api(request, post_uid):
    '''
    API endpoint to add a like to a post.

    ### `POST /api/posts/{post_id}/likes/add/`
    - **Purpose**: Adds a like to the specified post.
    - **When to Use**: When a user clicks "like" on a post.
    - **Why to Use**: Allows users to show appreciation for a post.

    #### Request
    - **Method**: POST
    - **URL Parameter**: `post_id` (string, required) - ID of the post.
    - **Body**: No additional fields required, as the current user is automatically set as the author.

    #### Response
    - **Success**: 201 Created - Returns the created like data.
    - **Error**: 400 Bad Request - If validation fails.
    '''

    """
    API endpoint to add a like to a post.
    """
    post = get_object_or_404(Post, uid=post_uid)
    print("post is found")

    if request.method == 'POST':
        data = request.data.copy()
        data['post'] = post.uid
        data['author'] = request.user.uid  # Current user as the like's author
        
        # Serialize and validate the like
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():

            print("Like serialiser is valid")
            print("Serialiser data: ", serializer.validated_data)
            
            # Save the like and increment the like count
            like = serializer.save(post=post, author=request.user)
            post.likes += 1
            post.save(update_fields=['likes'])

            
            like_data = {
                "type": "like",
                "author": SimpleAuthorSerializer(request.user).data,
                "published": like.created_at.isoformat(),  # ISO 8601 timestamp
                "id": f"{post.author.id}/liked/{like.id}",
                "object": post.id,   
                }

            print("like object created: ")
            #elif post is local:
            if (SERVER in post.author.id):
                print("POST IS LOCAL")
                #send to followers of the author
                #get all followers of author:
                followers = Follower.objects.filter(followed=request.user)
                # print("FOLLOWERS OF AUTHOR: ", [follower.follower.displayName for follower in followers])
                #compareHost = None
                for follower in followers:
                        try:
                            # Parse the follower's ID to get the base URL
                            follower_url = urlparse(follower.follower.id)
                            base_url = f"{follower_url.scheme}://{follower_url.netloc}/"
                            inbox_url = f"{follower.follower.id}/inbox"
                            
                           
                            # Retrieve the host_node
                            try:
                                host_node = Node.objects.get(host=base_url)
                                if not host_node.is_active or host_node.is_blocked:
                                    print(f"Node for host {base_url} is not active.")
                                    continue
                            except Node.DoesNotExist:
                                print(f"Node for host {base_url} does not exist.")
                                continue  # Skip to the next follower

                            print("FOLLOWER:", follower)
                            print("LIKE DATA:", like_data)        
                            #if compareHost != host_node:        
                            # Make the POST request to the inbox
                            response = requests.post(
                                    inbox_url,
                                    json=like_data,
                                    auth=(host_node.username, host_node.password),
                                    headers={'Content-Type': 'application/json'},
                                )
                            #     compareHost = host_node
                            # else: 
                            #     response = Response({"detail": "No need to add like at this node"}, status=status.HTTP_200_OK)
                            print("Response status code:", response.status_code)
                            print("Response content:", response.content)
                            if not (200 <= response.status_code < 300):
                                print(f"Failed to send to follower {follower.follower.uid}: {response.content}")

                        except Exception as e:
                            print(f"Failed to send like to follower {follower.follower.uid}: {str(e)}")
                        

            #if the post is remote:
            else:
                #send to inbox of author
                try:
                    ("sending like to remote author")
                    # Parse the author's ID to get the base URL
                    author_url = urlparse(post.author.id)
                    base_url = f"{author_url.scheme}://{author_url.netloc}/"
                    inbox_url = f"{post.author.id}/inbox"
                    
                    print("INBOX URL _______:", inbox_url)
                    # Retrieve the host_node
                    try:
                        host_node = Node.objects.get(host=base_url)
                        if not host_node.is_active or host_node.is_blocked:
                            print(f"Node for host {base_url} is not active.")
                            
                    except Node.DoesNotExist:
                        print(f"Node for host {base_url} does not exist.")
                        return Response("Node for host {base_url} does not exist", status=status.HTTP_400_BAD_REQUEST)
                        # Skip to the next follower

                    # Make the POST request to the inbox
                    print("LIKE DATA:", like_data)
                    response = requests.post(
                        inbox_url,
                        json=like_data,
                        auth=(host_node.username, host_node.password),
                        headers={'Content-Type': 'application/json'},
                    )
                    print("Response status code:", response.status_code)
                    #print("Response content:", response.content)
                    if not (200 <= response.status_code < 300):
                        print(f"Failed to send to follower {follower.follower.uid}: {response.content}")

                except Exception as e:
                    print(f"Failed to send like to follower {follower.follower.uid}: {str(e)}")

            return Response("like sent ",  status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#if i make a post and i like it,
#then that like is not getting propagated to follower

#but if i make post and follower likes it, i recieve likes



#get number of likes by post id
@swagger_auto_schema(
    method='get',
    operation_summary="Get like count for a post",
    operation_description="Retrieve the total number of likes for the specified post.",
    responses={
        200: openapi.Response(
            description="Success",
            examples={"application/json": {"like_count": 10}}
        ),
    }
)
@api_view(['GET'])
def get_like_count_api(request, post_uid):
    '''
    API endpoint to retrieve the like count for a specific post.

    ### `GET /api/posts/{post_id}/likes/count/`
    - **Purpose**: Provides the total number of likes for a post.
    - **When to Use**: For displaying like count on a post.
    - **Why to Use**: Shows the popularity of a post.

    #### Request
    - **Method**: GET
    - **URL Parameter**: `post_id` (string, required) - ID of the post.

    #### Response
    - **Success**: 200 OK - Returns a JSON object with `like_count`.
    '''
    post = get_object_or_404(Post, uid=post_uid)

    # object_url = request.build_absolute_uri(f'/posts/{post_id}')  # Dynamically build the URL
    
    #count likes directly using the post instance
    like_count = Like.objects.filter(post=post).count()
    print("likes count is: {}".format(like_count))

    return Response({'like_count': like_count}, status=status.HTTP_200_OK)


@api_view(['GET'])
def authorPostLikesView(request, author_uid, post_uid):

    # Retrieve the author or return a 404 if not found
    author = get_object_or_404(Author, uid=author_uid)

    # Retrieve the post or return a 404 if not found
    post = get_object_or_404(Post, uid=post_uid)

    # Retrieve all likes for the post and the author
    likes = Like.objects.filter(post=post)

    src = []
    for like in likes:
        like_data = {
            "type": "like",
            "author": {
                "type": "author",
                "id": author.id,
                "page": author.id,
                "host": author.id.split("/api/")[0],
                "displayName": author.displayName,
                "github": author.github,
                "profileImage": author.profileImage
            },
            "published": like.created_at,
            "id": f"http://nodeaaaa/api/authors/{author.uid}/liked/{like.id}",
            "object": f"http://nodeaaaa/api/authors/{author_uid}/posts/{post_uid}"
        }
        src.append(like_data)

    # Build the response object
    response_data = {
        "type": "likes",
        "page": f"http://nodeaaaa/authors/{author_uid}/posts/{post_uid}",
        "id": f"http://nodeaaaa/api/authors/{author_uid}/posts/{post_uid}/likes",
        "count": likes.count(),
        "src": src
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def authorPostCommentLikesView(request, author_uid, post_uid, comment_uid):
    #our code base does not support likes on comments themselves, 
    # so this always returns 0 likes on any comment id
    
    # Build the response object
    response_data = {
        "type": "likes",
        "page": f"http://nodeaaaa/authors/{author_uid}/posts/{post_uid}/comments/{comment_uid}",
        "id": f"http://nodeaaaa/api/authors/{author_uid}/posts/{post_uid}/comments/{comment_uid}/likes",
        "count": 0,
        "src": []
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def allLikedUIDView(request, author_uid):
    # Retrieve the author or return a 404 if not found
    author = get_object_or_404(Author, uid=author_uid)

    # Retrieve all likes made by the author
    likes = Like.objects.filter(author=author)

    # Build the `src` array for things liked by the author
    src = []
    for like in likes:
        like_data = {
            "type": "like",
            "author": {
                "type": "author",
                "id": f"http://nodeaaaa/api/authors/{author.uid}",
                "page": f"http://nodeaaaa/authors/{author.username}",
                "host": f"http://nodeaaaa/",
                "displayName": author.displayName,
                "github": author.github,
                "profileImage": author.profileImage
            },
            "published": like.created_at.isoformat(),
            "id": f"http://nodeaaaa/api/authors/{author.uid}/liked/{like.id}",
            "object": like.post.id  # The object they liked (e.g., post URL)
        }
        src.append(like_data)

    # Build the response object
    response_data = {
        "type": "likes",
        "id": f"http://nodeaaaa/api/authors/{author.uid}/liked",
        "page": f"http://nodeaaaa/authors/{author.uid}/liked",
        "count": likes.count(),
        "src": src
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def likedView(request, author_uid, like_uid):


    like = get_object_or_404(Like, id=like_uid)
    author = get_object_or_404(Author, uid=author_uid)

    # Build the like object
    like_data = {
        "type": "like",
        "author": {
            "type": "author",
            "id": author.id,
            "page": author.id,
            "host": author.id.split("/api/")[0],
            "displayName": author.displayName,
            "github": author.github,
            "profileImage": author.profileImage
        },
        "published": like.created_at,
        "id": f"{author.id}/liked/{like.id}",
        "object": like.post.id  # The object this like refers to (e.g., a post URL or comment URL)
    }

    return Response(like_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getCommentsByPostIDView(request, author_uid, post_uid):
    """
    API endpoint to retrieve all comments for a specific post in the required format.
    """

    # Retrieve the post or return a 404 if not found
    post = get_object_or_404(Post, uid=post_uid)

    # Retrieve comments related to the post, sorted by newest first
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    # Build the comments list manually
    src = []
    for comment in comments:
        comment_data = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": comment.author.id,
                "page": comment.author.id,
                "host": comment.author.id.split("/api/")[0],
                "displayName": comment.author.displayName,
                "github": comment.author.github,
                "profileImage": comment.author.profileImage,
            },
            "comment": comment.content,
            "contentType": comment.content_type,
            "published": comment.created_at,
            "id": f"http://nodeaaaa/api/authors/{comment.author.uid}/commented/{comment.id}",
            "post": f"http://nodebbbb/api/authors/{author_uid}/posts/{post_uid}",
            "page": f"http://nodebbbb/authors/{author_uid}/posts/{post_uid}",
            "likes": {
                "type": "likes",
                "id": f"http://nodeaaaa/api/authors/{comment.author.uid}/commented/{comment.id}/likes",
                "page": "",
                "page_number": 1,
                "size": 0,
                "count": 0,
                "src": [],
            },
        }
        src.append(comment_data)

    # Build the response object
    response_data = {
        "type": "comments",
        "page": f"http://nodebbbb/authors/{author_uid}/posts/{post_uid}",
        "id": f"http://nodebbbb/api/authors/{author_uid}/posts/{post_uid}/comments",
        "count": len(comments),
        "src": src,
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getCommentsByPostFQIDView(request, post_fqid):
    """
    API endpoint to retrieve all comments for a post using its Fully Qualified ID (FQID).
    
    ### `GET /api/posts/{POST_FQID}/comments`
    - **Purpose**: Retrieves comments for the specified post.
    - **Format**: Structured as a "comments" object as required.
    """

    # Extract the UID from the FQID (last part of the URL)
    post_uid = post_fqid.strip("/").split("/")[-1]

    # Retrieve the post or return a 404 if not found
    post = get_object_or_404(Post, uid=post_uid)

    # Retrieve comments related to the post, sorted by newest first
    comments = Comment.objects.filter(post=post)

    # Build the comments list manually
    src = []
    for comment in comments:
        comment_data = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": f"http://nodeaaaa/api/authors/{comment.author.uid}",
                "page": f"http://nodeaaaa/authors/{comment.author.username}",
                "host": "http://nodeaaaa/api/",
                "displayName": comment.author.displayName,
                "github": comment.author.github,
                "profileImage": comment.author.profileImage,
            },
            "comment": comment.content,
            "contentType": comment.content_type,
            "published": comment.created_at,
            "id": f"http://nodeaaaa/api/authors/{comment.author.uid}/commented/{comment.id}",
            "post": f"http://nodebbbb/api/posts/{post_fqid}",
            "page": f"http://nodebbbb/api/posts/{post_fqid}/comments",
            "likes": {
                "type": "likes",
                "id": f"http://nodeaaaa/api/authors/{comment.author.uid}/commented/{comment.id}/likes",
                "page": "",
                "page_number": 1,
                "size": 0,
                "count": 0,
                "src": [],
            },
        }
        src.append(comment_data)

    # Build the response object
    response_data = {
        "type": "comments",
        "page": f"http://nodebbbb/api/posts/{post_fqid}",
        "id": f"http://nodebbbb/api/posts/{post_fqid}/comments",
        "count": len(comments),
        "src": src,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getCommentByFQIDView(request, author_uid, post_uid, comment_fqid):
    """
    API endpoint to retrieve a single comment by its Fully Qualified ID (FQID).
    
    ### `GET /api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}`
    - **Purpose**: Retrieves a specific comment by its FQID.
    - **Format**: Returns a properly formatted "comment" object.
    """

    # Extract the UID from the FQID (last part of the URL)
    comment_uid = comment_fqid.strip("/").split("/")[-1]

    # Retrieve the comment or return a 404 if not found
    comment = get_object_or_404(Comment, id=comment_uid)

    # Build the comment object
    comment_data = {
        "type": "comment",
        "author": {
            "type": "author",
            "id": f"http://nodeaaaa/api/authors/{comment.author.uid}",
            "page": f"http://nodeaaaa/authors/{comment.author.username}",
            "host": "http://nodeaaaa/api/",
            "displayName": comment.author.displayName,
            "github": comment.author.github,
            "profileImage": comment.author.profileImage,
        },
        "comment": comment.content,
        "contentType": comment.content_type,
        "published": comment.created_at,
        "id": f"http://nodeaaaa/api/authors/{comment.author.uid}/commented/{comment.id}",
        "post": f"http://nodebbbb/api/authors/{author_uid}/posts/{post_uid}",
    }

    return Response(comment_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllCommentsByAuthorByUIDView(request, author_uid):
    """
    API endpoint to retrieve all comments made by a specific author.

    ### `GET /api/authors/{AUTHOR_UID}/comments`
    - **Purpose**: Retrieves all comments made by the specified author.
    - **Format**: Returns a list of properly formatted "comment" objects.
    """

    # Retrieve the author or return a 404 if not found
    author = get_object_or_404(Author, uid=author_uid)

    # Filter comments related to the author, sorted by newest first
    comments = Comment.objects.filter(author=author)

    # Build the comments list manually
    src = []
    for comment in comments:
        comment_data = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": f"http://nodeaaaa/api/authors/{author.uid}",
                "page": f"http://nodeaaaa/authors/{author.username}",
                "host": "http://nodeaaaa/api/",
                "displayName": author.displayName,
                "github": author.github,
                "profileImage": author.profileImage,
            },
            "comment": comment.content,
            "contentType": comment.content_type,
            "published": comment.created_at,
            "id": f"http://nodeaaaa/api/authors/{author.uid}/commented/{comment.id}",
            "post": f"http://nodebbbb/api/posts/{comment.post.uid}",
            "page": f"http://nodebbbb/api/authors/{comment.post.author.uid}/posts/{comment.post.uid}",
        }
        src.append(comment_data)

    # Build the response object
    response_data = {
        "type": "comments",
        "page": f"http://nodeaaaa/authors/{author_uid}/comments",
        "id": f"http://nodeaaaa/api/authors/{author_uid}/comments",
        "count": len(comments),
        "src": src,
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getCommentedCommentByUIDView(request, author_uid, comment_uid):
    """
    API endpoint to retrieve a single comment by its UID, authored by a specific author.

    ### `GET /api/authors/{AUTHOR_UID}/commented/{COMMENT_UID}`
    - **Purpose**: Retrieves a specific comment authored by the specified author.
    - **Format**: Returns a properly formatted "comment" object.
    """

    # Retrieve the comment or return a 404 if not found
    comment = get_object_or_404(Comment, id=comment_uid)

    # Build the comment object
    comment_data = {
        "type": "comment",
        "author": {
            "type": "author",
            "id": f"http://nodeaaaa/api/authors/{comment.author.uid}",
            "page": f"http://nodeaaaa/authors/{comment.author.username}",
            "host": "http://nodeaaaa/api/",
            "displayName": comment.author.displayName,
            "github": comment.author.github,
            "profileImage": comment.author.profileImage,
        },
        "comment": comment.content,
        "contentType": comment.content_type,
        "published": comment.created_at,
        "id": f"http://nodeaaaa/api/authors/{author_uid}/commented/{comment_uid}",
        "post": f"http://nodebbbb/api/posts/{comment.post.uid}",
        "page": f"http://nodebbbb/api/authors/{comment.author.uid}/posts/{comment.post.uid}",
    }

    return Response(comment_data, status=status.HTTP_200_OK)
