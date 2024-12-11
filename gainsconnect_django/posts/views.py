from urllib.parse import urlparse
from django.shortcuts import get_object_or_404
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Post
from follow.models import Follower
from .serializers import PostSerializer
from django.db.models import Q
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .swagger import swagger_docs
from follow.models import Friends
from authors.serializers import SimpleAuthorSerializer
from inbox.views import InboxView
from django.urls import reverse
from rest_framework.test import APIClient
from node.models import Node
from authors.models import Author
from rest_framework_simplejwt.authentication import JWTAuthentication
from node.views import NodeAuthentication
from gainsconnect_django.views import parseURL
from gainsconnect_django.settings import SERVER

@swagger_auto_schema(swagger_docs['delete_post'])
@api_view(['DELETE'])
def delete_post(request, post_uid):
    print("recevied delete request")
    try:
        post = Post.objects.get(uid=post_uid)
    except:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
    if post.author.id != request.user.id:
        return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    post.is_deleted = True
    post.visibility = 'DELETED'
    post.save()

    serializer = PostSerializer(post, data=request.data, partial=True, context={'author': request.user}) #partially update the post wth new data
    if serializer.is_valid():
        serializer.save()

        post_data = {
            'type': 'post',
            'title': post.title,
            'id': post.id,
            'description': post.description,
            'contentType': post.contentType,
            'content': post.content,
            'author': SimpleAuthorSerializer(request.user).data,
            'published': post.published.isoformat(),
            'visibility': post.visibility,
            'likes': {},
            'comments': {},
        }

        if post.visibility == "PUBLIC":
            #send post to inbox of all nodes
            nodes = Node.objects.filter(is_active=True).filter(is_blocked=False)
            for node in nodes:
                try:
                    # Assuming each node has a base URL stored
                    base_url = node.host + 'api/'

                    authors = Author.objects.filter(host=base_url)
                    for author in authors:
                        inbox_url = f"{author.id}/inbox"
                        print("author inbox_url", inbox_url)

                        response = requests.post(
                            inbox_url,
                            json=post_data,
                            auth=(node.username, node.password),
                            headers={'Content-Type': 'application/json'},
                        )

                        print("sent")
                        print("response", response)
                        if not 200 <= response.status_code < 300:
                            print(f"Failed to send to author {author.displayName}: {response.content}")
                                
                except Exception as e:
                    print(f"Failed to send to node {node}: {str(e)}")
            
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        
        else:
            followers = Follower.objects.filter(followed=request.user)
            for follower in followers:
                try:
                    follower_url = urlparse(follower.follower.id)
                    base_url = f"{follower_url.scheme}://{follower_url.netloc}/"

                    # if base_url in updated_servers:
                    #     continue

                    inbox_url = f"{follower.follower.id}/inbox"

                    try:
                        host_node = Node.objects.get(host=base_url)
                        if not host_node.is_active or host_node.is_blocked:
                            print(f"Node for host {base_url} is not active.")
                            continue
                        elif host_node.host == SERVER:
                            print(f"Node for host {base_url} is local.")
                            continue
                    except Node.DoesNotExist:
                        print(f"Node for host {base_url} does not exist.")
                        continue

                    response = requests.post(
                        inbox_url,
                        json=post_data,
                        auth=(host_node.username, host_node.password),
                        headers={'Content-Type': 'application/json'},
                    )

                    print("sent")
                    print("response", response)
                    if 200 <= response.status_code < 300:
                        print(f"Successfully sent to follower {follower.follower.uid}")
                    else:
                        print(f"Failed to send to follower {follower.follower.uid}: {response.content}")
                except Exception as e:
                    print(f"Failed to send to follower {follower.follower.uid}: {str(e)}")
            
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(swagger_docs['post_list_get'])
@swagger_auto_schema(swagger_docs['post_list_post'])
@api_view(['GET','POST'])
def post_list_creation(request):
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-published')
        serializer = PostSerializer(posts, many = True, context={'author': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data, context={'author': request, 'request': request})
        print("request", request.data)
        print("serializer initial data", serializer.initial_data)

        if serializer.is_valid():
            print("serializer data", serializer.validated_data)
            post = serializer.save(author=request.user)
            print("post", post)

            post_data = {
                'type': 'post',
                'title': post.title,
                'id': post.id,
                'description': post.description,
                'contentType': post.contentType,
                'content': post.content,
                'author': SimpleAuthorSerializer(request.user).data,
                'published': post.published.isoformat(),  # Convert datetime to string
                'visibility': post.visibility,
                'likes': {},
                'comments': {},
            }

            if post.visibility == 'UNLISTED':
                # send post to inbox of followers
                followers = Follower.objects.filter(followed=request.user)
                print("followers:", followers)
                
                if followers:
                    for follower in followers:
                        print("follower:", follower)
                        try:
                            # Parse the follower's ID to get the base URL
                            follower_url = urlparse(follower.follower.id)
                            print("follower_url", follower_url)
                            base_url = f"{follower_url.scheme}://{follower_url.netloc}/"
                            print("base_url", base_url)
                            inbox_url = f"{follower.follower.id}/inbox"
                            print("inbox_url", inbox_url)
                        
                            # Retrieve the host_node
                            try:
                                host_node = Node.objects.get(host=base_url)
                                if not host_node.is_active or host_node.is_blocked:
                                    print(f"Node for host {base_url} is not active.")
                                    continue
                            except Node.DoesNotExist:
                                print(f"Node for host {base_url} does not exist.")
                                continue  # Skip to the next follower

                            # Make the POST request to the inbox
                            response = requests.post(
                                inbox_url,
                                json=post_data,
                                auth=(host_node.username, host_node.password),
                                headers={'Content-Type': 'application/json'},
                            )
                            print("Response status code:", response.status_code)
                            print("Response content:", response.content)
                            if not (200 <= response.status_code < 300):
                                print(f"Failed to send to follower {follower.follower.uid}: {response.content}")

                        except Exception as e:
                            print(f"Failed to send to follower {follower.follower.uid}: {str(e)}")
                                    
            elif post.visibility == 'FRIENDS':
                friends = Friends.objects.filter(Q(author1=request.user) | Q(author2=request.user))

                if friends:
                    for friend in friends:
                        try:
                            friend_user = friend.author2 if friend.author1 == request.user else friend.author1
                            # Parse the friend's ID to get the base URL
                            friend_url = urlparse(friend_user.id)
                            print("friend_url", friend_url)
                            base_url = f"{friend_url.scheme}://{friend_url.netloc}/"
                            print("base_url", base_url)
                            inbox_url = f"{friend_user.id}/inbox"
                            print("inbox_url", inbox_url)

                            # Retrieve the host_node
                            try:
                                host_node = Node.objects.get(host=base_url)
                                if not host_node.is_active or host_node.is_blocked:
                                    print(f"Node for host {base_url} is not active.")
                                    continue
                            except Node.DoesNotExist:
                                print(f"Node for host {base_url} does not exist.")
                                continue  # Skip to the next follower

                            print("post_data", post_data)
                            # Make the POST request to the inbox
                            response = requests.post(
                                inbox_url,
                                json=post_data,
                                auth=(host_node.username, host_node.password),
                                headers={'Content-Type': 'application/json'},
                                # content_type='application/json'
                            )
                            print("response", response)
                            if response.status_code != status.HTTP_200_OK:
                                print(f"Failed to send to friend {friend.author2.uid}: {response.content}")

                        except Exception as e:
                            print(f"Failed to send to friend {friend.author2.uid}: {str(e)}")
            
            else:
                nodes = Node.objects.filter(is_active=True).filter(is_blocked=False)
                print("sending public post")
                print("nodes", nodes)
                for node in nodes:
                    print("node", node)
                    try:
                        # Assuming each node has a base URL stored
                        base_url = node.host + 'api/'
                        print("base_url", base_url)

                        # Retrieve all authors associated with the node
                        authors = Author.objects.filter(host=base_url)
                        
                        for author in authors:
                            inbox_url = f"{author.id}/inbox"
                            print("author inbox_url", inbox_url)

                            print("post_data", post_data)
                            # Make the POST request to the inbox
                            response = requests.post(
                                inbox_url,
                                json=post_data,
                                auth=(node.username, node.password),
                                headers={'Content-Type': 'application/json'},
                                # content_type='application/json'
                            )
                            print("sent")
                            print("response", response)
                            if response.status_code != status.HTTP_200_OK:
                                print(f"Failed to send to author {author.displayName}: {response.content}")

                    except Exception as e:
                        print(f"Failed to send to node {node}: {str(e)}")
                    
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(swagger_docs['edit_post'])
@api_view(['PUT'])
def edit_post(request, post_uid):
    print("request for editing post")
    try:
        post = Post.objects.get(uid=post_uid)
    except:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PostSerializer(post, data=request.data, partial=True, context={'author': request.user}) #partially update the post wth new data
    if serializer.is_valid():
        print("data is valid")
        serializer.save()
        print("changes saved")
        post_data = {
            'type': 'post',
            'title': post.title,
            'id': post.id,
            'description': post.description,
            'contentType': post.contentType,
            'content': post.content,
            'author': SimpleAuthorSerializer(request.user).data,
            'published': post.published.isoformat(),
            'visibility': post.visibility,
            'likes': {},
            'comments': {},
        }

        if post.visibility == "PUBLIC":
            #send post to inbox of all nodes
            nodes = Node.objects.filter(is_active=True).filter(is_blocked=False)
            for node in nodes:
                try:
                    # Assuming each node has a base URL stored
                    base_url = node.host + 'api/'

                    authors = Author.objects.filter(host=base_url)
                    for author in authors:
                        inbox_url = f"{author.id}/inbox"
                        print("author inbox_url", inbox_url)

                        response = requests.post(
                            inbox_url,
                            json=post_data,
                            auth=(node.username, node.password),
                            headers={'Content-Type': 'application/json'},
                        )

                        print("sent")
                        print("response", response)
                        if not 200 <= response.status_code < 300:
                            print(f"Failed to send to author {author.displayName}: {response.content}")
                                
                except Exception as e:
                    print(f"Failed to send to node {node}: {str(e)}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            followers = Follower.objects.filter(followed=request.user)
            for follower in followers:
                try:
                    follower_url = urlparse(follower.follower.id)
                    base_url = f"{follower_url.scheme}://{follower_url.netloc}/"

                    # if base_url in updated_servers:
                    #     continue

                    inbox_url = f"{follower.follower.id}/inbox"

                    try:
                        host_node = Node.objects.get(host=base_url)
                        if not host_node.is_active or host_node.is_blocked:
                            print(f"Node for host {base_url} is not active.")
                            continue
                        elif host_node.host == SERVER:
                            print(f"Node for host {base_url} is local.")
                            continue
                    except Node.DoesNotExist:
                        print(f"Node for host {base_url} does not exist.")
                        continue

                    response = requests.post(
                        inbox_url,
                        json=post_data,
                        auth=(host_node.username, host_node.password),
                        headers={'Content-Type': 'application/json'},
                    )

                    print("sent")
                    print("response", response)
                    if not 200 <= response.status_code < 300:
                        print(f"Failed to send to follower {follower.follower.uid}: {response.content}")
                except Exception as e:
                    print(f"Failed to send to follower {follower.follower.uid}: {str(e)}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(swagger_docs['profile_posts_view'])
class ProfilePostsView(APIView):
    authentication_classes = [JWTAuthentication, NodeAuthentication]

    def get(self, request, *args, **kwargs):
        request_authorization = request.headers.get('Authorization', '')
        print("received authorization", request_authorization)

        fid = kwargs.get('fid') or kwargs.get('uid')
        print("fid", fid)

        if ('Bearer' in request_authorization):
            print("received request from frontend")
            if ('http' in fid):
                # if author is local
                if (SERVER in fid):
                    print("author is local")
                    fid_uuid = parseURL(fid)
                    print("url_fid", fid_uuid)
                    try:
                        # if user is viewing their own profile
                        print("user", request.user)
                        if request.user.id == fid:
                            print("user is the same as the author id")
                            posts = Post.objects.filter(author=request.user, is_deleted=False).order_by('-published')
                        else:
                            # fetch all public posts of the author
                            posts = Post.objects.filter(author=fid_uuid, visibility="PUBLIC", is_deleted=False).order_by('-published')

                        print("posts", posts)
                        serializer = PostSerializer(posts, many=True)
                        response = {
                            'type': 'posts',
                            'src': serializer.data
                        }
                        return Response(response, status=status.HTTP_200_OK)

                    except Post.DoesNotExist:
                        return Response({"error": "No posts found for this author"}, status=status.HTTP_404_NOT_FOUND)
                
                # if author is remote
                else:
                    print("author is remote")
                    parse = urlparse(fid)
                    host = f"{parse.scheme}://{parse.netloc}/"
                    remote_uid = parseURL(fid)
                    host_node = get_object_or_404(Node, host=host)
                    print("host_node", host_node.name)
                    print("remote_uid", remote_uid)
                    
                    # get all posts of the author
                    response = requests.get(
                        f"{host_node.host}api/authors/{remote_uid}/posts/", 
                        auth=(host_node.username, host_node.password))
                    print("response", response)
                    try:
                        content = response.json()
                    except requests.exceptions.JSONDecodeError:
                        print(f"Invalid JSON response: {response.content}")
                    print("response content:", content)

                    if len(content['src']) == 0:
                        return Response({'src': []}, status=status.HTTP_200_OK)
                    
                    author_data = content['src'][0].get('author', {})
                    print("author data", author_data)
                    author_id_url = author_data.get('id')
                    print("author id url", author_id_url)

                    # Check if the author already exists
                    try:
                        author = Author.objects.get(id=author_id_url)
                    except Author.DoesNotExist:
                        print("Author does not exist, attempting to create a new one.")
                        try:
                            # Use create_remote_author to handle UUID validation and creation
                            author = Author.objects.create_remote_author(author_data)
                            print("Created new author:", author.uid)
                        except Exception as e:
                            print("Error creating author:", e)
                            return Response({"error": "Failed to create author"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
                    # create posts in local database
                    for post in content['src']:
                        post_id = post.get('id')
                        print("post id", post_id)
                        if Post.objects.filter(id=post_id).exists():
                            print("post already exists", post_id)
                            continue

                        serializer = PostSerializer(data=post, context={'author': author})
                        print("initial data:",serializer.initial_data)
                        if serializer.is_valid():
                            try:
                                post = serializer.save()
                                print("Post created successfully:", post)
                            except Exception as e:
                                print("An error occurred while creating the post:", e)
                                return Response({"error": "Failed to create post"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            print("Validation errors:", serializer.errors)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    return Response(content, status=status.HTTP_200_OK)
        
        # assumes uid will be in the api endpoint and not fid
        elif ('Basic' in request_authorization):
            print("received request from node")
            if 'http' in fid:
                print("fid is a id")
                author = Author.objects.get(id=fid)
                posts = Post.objects.filter(author=author, visibility="PUBLIC", is_deleted=False).order_by('-published')
            else:
                print("fid is a uid")
                author = Author.objects.get(uid=fid)
                posts = Post.objects.filter(author=author, visibility="PUBLIC", is_deleted=False).order_by('-published')
            serializer = PostSerializer(posts, many=True)
            print("posts fetched", serializer.data)
            response = {
                'type': 'posts',
                'src': serializer.data
            }   
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response("Require Basic or Bearer authorization", status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(swagger_docs['stream_view'])
class StreamView(APIView):
    def get(self, request):
        #get the current author
        author = request.user

        #get the authors the current user is following
        followed_authors = Follower.objects.filter(follower=author).values_list('followed', flat=True)

        #get the authors the current user is friends with
        friends = Friends.objects.filter(Q(author1=author) | Q(author2=author))
        friend_ids = [friend.author2.id if friend.author1 == author else friend.author1.id for friend in friends]

        #get posts from followed authors (with visibility friends or visibility unlisted)
        followed_posts = Post.objects.filter(
            Q(author__in=followed_authors) & 
            (Q(visibility='UNLISTED')),
            is_deleted=False
        )

        friends_posts = Post.objects.filter(author__id__in=friend_ids, visibility='FRIENDS', is_deleted=False)
        print("friends posts", friends_posts)

        #get public posts excluding user's posts
        public_posts = Post.objects.filter(visibility='PUBLIC', is_deleted=False).exclude(author=author)

        #get user's own posts
        user_posts = Post.objects.filter(author=author, is_deleted=False)

        #combine followed and public posts
        combined_posts = public_posts.union(followed_posts).union(user_posts).union(friends_posts)

        order_posts = combined_posts.order_by('-updated_at')

        #serialize the combined posts
        serializer = PostSerializer(order_posts, many=True, context={'request': request})

        print("serializer data", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RepostView(APIView):
    @swagger_auto_schema(**swagger_docs["repost_post"])
    def post(self, request):
        """
        ### `POST /posts/repost/`
        - **Purpose**: Creates a repost of an existing post.
        - **When to Use**: For sharing an existing post under a new author.
        - **Why to Use**: Enables content sharing across the platform.

        #### Request
        - **Method**: POST
        - **Body**:
        - `original_post_id` (string, required) - ID of the post to repost.

        #### Response
        - **Success**: 200 OK - Returns repost details if successful.
        - **Error**: 400 Bad Request - If `original_post_id` is missing or invalid.
        """
        # create new post, set original post field with id/url to original post, set description if there is any
        data = request.data
        author = request.user
        originalPostID = data.get('original_post_id')
        originalPost = get_object_or_404(Post, pk=originalPostID)

        if not originalPost or not author:
            return Response({"error": "Author ID and Original post ID are invalid."}, status=status.HTTP_400_BAD_REQUEST)
        
        newPost = Post.objects.create(
            author = author,
            visibility = 'unlisted',
            contentType = 'text/plain',
            original_post = originalPost,
        )
        
        serializer = PostSerializer(newPost, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(swagger_docs['post_detail_view'])
class PostDetailView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication, NodeAuthentication]

    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all() #allowing access to posts that exist

    def get(self, request, *args, **kwargs):
        #get author and post id from url
        print("request for post details")
        author_uid = self.kwargs.get('author_uid')
        post_uid = self.kwargs.get('post_uid')
        print("author uid", author_uid)
        print("post uid", post_uid)
        
        author = get_object_or_404(Author, uid=author_uid)
        print("author", author)
        post = get_object_or_404(Post, uid=post_uid)
        print("post", post)

        serializer = PostSerializer(post)
        print("serializer data", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            # Retrieve the post by author and post ID
            post = self.get_queryset().get(author__uid=author_uid, uid=post_uid, is_deleted=False)
        
            #logic to handle post visibility
            if post.visibility == "PUBLIC":
                serializer = self.get_serializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif post.visibility == "FRIENDS":
                author = request.user

                is_friend = Friends.objects.filter(
                    Q(author1=author, author2=post.author) |
                    Q(author1=post.author, author2=author)
                ).exists()

                if is_friend:
                    serializer = self.get_serializer(post)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    # deny access if they are not friends
                    raise PermissionDenied({"error": "You are not authorized to view this post."})
            else:
                # Handle other visibility types if necessary
                raise PermissionDenied({"error": "You are not authorized to view this post."})
        except Post.DoesNotExist:
            raise NotFound({"error": "Post not found"})
