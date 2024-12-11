from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from authors.models import Author
from authors.serializers import SimpleAuthorSerializer
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from .swagger import swagger_docs
from gainsconnect_django.settings import SERVER
from gainsconnect_django.views import parseURL
from urllib.parse import unquote
import requests
from requests.exceptions import Timeout
from node.models import Node
from node.views import NodeAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
import uuid
from copy import deepcopy
from urllib.parse import urlparse
from posts.models import Post


class FollowRequestView(APIView):

    @swagger_auto_schema(**swagger_docs["follow_request_post"])
    def post(self, request: Request) -> Response:
        """Creates a new follow request

        Args:
            request (Request): The HTTP request object containing actor and object
                actor (str): The ID of the user who sent the request
                object (str): The ID of the author who is receiving the request

        Returns:
            Response: A response containing errors or success message
        """
        object_data = request.data['object']

        # local
        if (SERVER in object_data['id']):
            print("local")
            # create the serializer
            objectUID = parseURL(object_data['id'])
            data = {
                "actor": request.data['actor'],
                "object": objectUID
            }
            serializer = FollowRequestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response("request created", status=status.HTTP_201_CREATED)
            else:
                print("serializer is not valid", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # remote
        else:
            print("remote")

            # Try to find existing remote author, create if doesn't exist
            try:
                remote_author = Author.objects.get(id=object_data['id'])
            except Author.DoesNotExist:
                remote_author = Author.objects.create_remote_author(object_data)
                print("remote author created")
            # create follow request object
            data = {
                "actor": request.data['actor'],
                "object": str(remote_author.uid),
            }
            serializer = FollowRequestSerializer(data=data)
            serializer_copy = deepcopy(serializer)
            # validate and send to remote node
            if serializer.is_valid() and serializer_copy.is_valid():
                print("serializer is valid", serializer_copy.data)

                # send to remote inbox
                parse = urlparse(object_data['host'])
                host = f"{parse.scheme}://{parse.netloc}/"
                print("host", host)
                host_node = Node.objects.filter(host=host).first()
                foreign_id = parseURL(object_data['id'])
                response = requests.post(
                    f'{host_node.host}api/authors/{foreign_id}/inbox', 
                    auth=(host_node.username, host_node.password), 
                    json=serializer_copy.data
                    )
                
                # if sending to remote node that is not gainsconnect
                if 'gains' not in host:
                    print("sending to non-gainsconnect node")
                    actor = get_object_or_404(Author, uid=request.data['actor'])
                    # Create follower object
                    Follower.objects.create(follower=actor, followed=remote_author)

                    # check if they are following user, then create friend relation
                    return Response("follower created", status=status.HTTP_201_CREATED)

                # if there is a response body
                try:
                    content = response.json()
                except requests.exceptions.JSONDecodeError:
                    print(f"Invalid JSON response: {response.content}")
                print("response content:", content)

                # handle response
                if 200 <= response.status_code < 300:
                    serializer.save()
                    print(f"follow request created {response.status_code}")
                    return Response("request created", status=status.HTTP_201_CREATED)
                else:
                    print("failed posting to inbox", response.json())
                    return Response(response.json(), status=response.status_code)
            else:
                print("serializer is not valid", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(**swagger_docs["follow_request_get"])
    def get(self, _, uid: str) -> Response:
        """Retrieve follow requests for a specific author

        Args:
            id (str): ID of the author

        Returns:
            response: A JSON array of all the follow requests
        """
        receiver = get_object_or_404(Author, pk=uid)
        requests = receiver.received_request.all()
        senders = [request.actor for request in requests]
        serializer = SimpleAuthorSerializer(senders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class HandleRequestView(APIView):
    authentication_classes = [JWTAuthentication, NodeAuthentication]

    @swagger_auto_schema(**swagger_docs["handle_request_post"])
    def post(self, request: Request) -> Response:
        """Decline a follow request based on user's response

        Args:
            request (Request): Contains actor ID, object ID, and reply to follow request
                actor (str): ID of actor
                object (str): ID of object
                reply (bool): Reply to request

        Returns:
            Response: JSON response with either success or error message
        """
        actorURL = unquote(request.data['actor'])
        # retrieve the associated objects
        object = get_object_or_404(Author, pk=request.data['object'])      # the one that is receiving the request
        actor = get_object_or_404(Author, id=actorURL)     # the one that is sending the request
        followRequest = object.received_request.get(actor=actor)

        # if user declined follow request
        if request.data['reply'] == False:
            followRequest.delete()
            return Response('Declined request', status=status.HTTP_200_OK)
        else:
            return Response('Invalid request', status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(**swagger_docs["handle_request_put"])
    def put(self, _, uid: str, fid: str):
        '''
        Creates a follow object, with uid as the followed and fid as the follower,
        sends posts to the new follower if they are remote
        '''
        # retrieve the associated objects
        object = get_object_or_404(Author, pk=uid)      # the one that is receiving the request
        actor = get_object_or_404(Author, id=fid)  # the one that is sending the request

        # delete follow request
        followRequest = object.received_request.get(actor=actor)
        followRequest.delete()

        # create the follow object
        Follower.objects.create(follower=actor, followed=object)
        
        # check if friend relation exists and create
        relation = Follower.objects.filter(follower=object, followed=actor)
        if relation:
            Friends.objects.create(author1=object, author2=actor)
            relation_status = "Friends"
            print("this the friends relation part@@@@")
        else: 
            relation_status = "Following"
            print("this is the following relation part@@@@")

        # check if new follower is remote
        if SERVER in fid:
            print("new follower is local")
            return Response('Request accepted', status=status.HTTP_201_CREATED)
        else:
            print("new follower is remote")
        
            post_list = []
            posts = Post.objects.filter(author=object, is_deleted=False)
            if relation_status == "Following":
                posts = posts.exclude(visibility="FRIENDS") #send all posts except friends
                print("this is the posts part@@@@")
            for post in posts:
                post_data = {
                'type': 'posts',
                'title': post.title,
                'id': post.id,
                'description': post.description,
                'contentType': post.contentType,
                'content': post.content,
                'author': SimpleAuthorSerializer(post.author).data,
                'published': post.published.isoformat(),
                'visibility': post.visibility,
                }
                post_list.append(post_data)
                print("THIS IS AN INDIVIDUAL POST@@@@@@@", post_data)
            print("post_list@@@@@@@", post_list)

            
            # Send the list of posts to the new follower's inbox
            try:
                # Construct the inbox URL for the new follower
                follower_url = urlparse(actor.id)
                base_url = f"{follower_url.scheme}://{follower_url.netloc}/"
                inbox_url = f"{base_url}api/authors/{actor.uid}/inbox"

                # Retrieve the host_node
                host_node = Node.objects.get(host=base_url)
                print("This is the host_node@@@@@@@", host_node)
                # Make the POST request to the inbox with the list of posts
                response = requests.post(
                    inbox_url,
                    json={'type': 'posts', 'items': post_list},
                    auth=(host_node.username, host_node.password),
                    headers={'Content-Type': 'application/json'},
                )
                print("This is the response@@@@@", response)
                if 200 <= response.status_code < 300:
                    print("posts sent to follower")
                else:
                    print(f"Failed to send posts to follower {actor.uid}: {response.content}")
            except Exception as e:
                print(f"Failed to send posts to follower {actor.uid}: {str(e)}")
                return Response(f"Failed to send posts to follower {actor.uid}: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response('Request accepted', status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(**swagger_docs["handle_request_delete"])
    def delete(self, _, uid: str, fid: str):
        """ Unfollows an author

        Args:
            uid (str): uid of the current user
            fid (str): id of the author that sent the request

        Returns:
            response: A response indicating success
        """
        print("unfollowing")

        # get associated objects
        object = get_object_or_404(Author, pk=uid)      # the one that following
        actor = get_object_or_404(Author, id=fid)       # the one that is being followed 

        followRequest = get_object_or_404(Follower, follower=object, followed=actor)
        followRequest.delete()

        # find and delete friend object if it exists
        friendship = Friends.objects.filter(
            (Q(author1=object) & Q(author2=actor)) |
            (Q(author1=actor) & Q(author2=object))
        )
        if friendship.exists():
            friendship.first().delete()

        # delete object
        return Response('Unfollowed author', status=status.HTTP_204_NO_CONTENT)

    
    @swagger_auto_schema(**swagger_docs["handle_request_get"])
    def get(self, request, uid: str, fid: str):
        '''
        Checks the relationship between two authors
        '''
        request_authorization = request.headers.get('Authorization', '')
        print("received authorization", request_authorization)
        user = get_object_or_404(Author, pk=uid)
        author = get_object_or_404(Author, id=fid)
        
        # request from frontend
        if ('Bearer' in request_authorization):
            print("received request from frontend")
            # if fid is a local author
            if (SERVER in fid):
                print("checking relation on local author")
                author = get_object_or_404(Author, id=fid)
                serializer = ExploreUsersSerializer(author, context={'author': user})
                relation = serializer.data['relation']
            # if fid is a remote author
            else:
                print("checking relation on remote author")
                # get relation from remote node
                parse = urlparse(fid)
                host = f"{parse.scheme}://{parse.netloc}/"
                remote_uid = parseURL(fid)
                print("fid", remote_uid)
                host_node = get_object_or_404(Node, host=host)

                try:
                    response = requests.get(
                        f"{host_node.host}api/authors/{remote_uid}/followers/{user.id}", 
                        auth=(host_node.username, host_node.password),
                        timeout=10
                    )
                except Timeout: 
                    return Response("Request timed out", status=status.HTTP_408_REQUEST_TIMEOUT)
                except ConnectionError:
                    return Response("Connection error", status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
                # if there is a response body
                try:
                    relation = response.json()
                except requests.exceptions.JSONDecodeError:
                    print(f"Invalid JSON response: {response.content}")
                    relation = None
                print("relation", relation)

                # scenario where user has sent request and author accepted, going from NONE -> FOLLOWING or FRIENDS
                if relation == "FOLLOWING" or relation == "FRIENDS" or response.status_code == 200:
                    # get follow request if exists
                    follow_request = FollowRequest.objects.filter(actor=user, object=author).first()
                    if follow_request is not None:
                        follow_request.delete()
                        # create follow object
                        Follower.objects.create(follower=user, followed=author)
                        # if there is no response body
                        if relation is None and response.status_code == 200:
                            relation = "FOLLOWING"
                    # scenario where author unfollows user, going from FRIENDS -> FOLLOWING
                    if relation == "FOLLOWING":
                        # check for friendship
                        friendship = Friends.objects.filter(
                        (Q(author1=user) & Q(author2=author)) |
                            (Q(author1=author) & Q(author2=user))
                        )
                        # delete friendship if it exists
                        if friendship.exists():
                            friendship.delete()
                            # delete reverse follower relation
                            reverse_relation = Follower.objects.filter(follower=author, followed=user).first()
                            if reverse_relation is not None:
                                reverse_relation.delete()
                    # check if reverse follower and friend relation exists 
                    reverse_relation = Follower.objects.filter(follower=author, followed=user).first()
                    friendship = Friends.objects.filter(
                        (Q(author1=user) & Q(author2=author)) |
                        (Q(author1=author) & Q(author2=user))
                    )
                    # create friendship if needed
                    if reverse_relation is not None and not friendship.exists():
                        Friends.objects.create(author1=user, author2=author)
                        relation = "FRIENDS"

                elif relation == "NONE" or relation is None:
                    # check for follow request
                    follow_request = FollowRequest.objects.filter(actor=user, object=author).first()
                    if follow_request is not None:
                        follow_request.delete()

                    # check for follower relation
                    follower = Follower.objects.filter(follower=author, followed=user).first()
                    if follower is not None:
                        follower.delete()

                    # check for friend relation
                    friendship = Friends.objects.filter(
                        (Q(author1=user) & Q(author2=author)) |
                        (Q(author1=author) & Q(author2=user))
                    )
                    if friendship.exists():
                        friendship.delete()
                else:
                    return Response("Relation check on remote node returned 404", status=status.HTTP_404_NOT_FOUND)
                
        # request from a remote node
        elif ('Basic' in request_authorization):
            print("received request from remote node")
            serializer = ExploreUsersSerializer(user, context={'author': author})
            relation = serializer.data['relation']
        else:
            return Response("Require Basic or Bearer authorization", status=status.HTTP_401_UNAUTHORIZED)
        
        # return relation
        if relation == "NONE" or relation == "PENDING":
            return Response(relation, status=status.HTTP_404_NOT_FOUND)
        return Response(relation, status=status.HTTP_200_OK)

class GetFollowersView(APIView):

    @swagger_auto_schema()
    def get(self, _, uid: str) -> Response:
        """Gets a list of authors who are uid's followers

        Args:
            uid (str): uid of the author

        Returns:
            Response: list of authors
        """
        author = get_object_or_404(Author, pk=uid)
        followedList = author.followed.all()
        authors = [entry.follower for entry in followedList]
        serializer = FollowListSerializer({'followers': authors})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListFollower(APIView):

    @swagger_auto_schema(**swagger_docs["list_follower_get"])
    def get(self, _, id: str, category: str) -> Response:
        """Gets a list of followers, following, or friends for an author

        Args:
            id (str): ID of author to retrieve list for
            category (str): Category of list, (following, followed, friends)

        Returns:
            response: A JSON array of authors within the corresponding category
        """
        author = get_object_or_404(Author, pk=id)

        # gets the list of authors the user is following
        if category == 'following':
            followingList = author.following.all()
            authors = [entry.followed for entry in followingList]
            serializer = SimpleAuthorSerializer(authors, many=True)

        # gets the list of authors the user is friends with
        elif category == 'friends':
            # have to search both fields to get entire list
            friends1 = author.friend1.all()
            friends2 = author.friend2.all()
            friendsList1 = [friendship.author2 for friendship in friends1]
            friendsList2 = [friendship.author1 for friendship in friends2]
            friendsList = friendsList1 + friendsList2
            serializer = SimpleAuthorSerializer(friendsList, many=True)
        
        else:
            return Response("Invalid category", status=status.HTTP_400_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ExploreAuthors(APIView):

    @swagger_auto_schema(**swagger_docs["explore_authors_get"])
    def get(self, _, uid: str) -> Response:
        """Gets a list of all the other authors on the node

        Args:
            uid (str): UID of current user to exclude from response

        Returns:
            response: A JSON array of all authors on the node
        """
        user = get_object_or_404(Author, pk=uid)
        local_authors = Author.objects.exclude(uid=uid).exclude(is_remote=True).exclude(is_staff=True)
        all_authors = list(local_authors)

        # get authors from remote nodes
        for node in Node.objects.filter(is_active=True):
            print("retrieving from", node.host)
            try:
                response = requests.get(
                    node.host + "api/authors/", 
                    auth=(node.username, node.password),
                    timeout=10
                )   
                # create temporary author objects 
                if response.status_code == 200:
                    remote_authors = response.json()
                    print("remote authors", remote_authors)
                    for author in remote_authors['authors']:
                        print("author", author)
                        if author['id'] is None:
                            continue

                        # In case profileImage is none or empty
                        profile_image = author.get('profileImage')
                        if profile_image in [None, '', "''", '""', "''"]:
                            profile_image = 'https://i.imgur.com/V4RclNb.png'

                        remote_author = Author(
                            uid=uuid.uuid4(),
                            id=author['id'],
                            displayName=author['displayName'],
                            profileImage=profile_image,
                            host=author['host'],
                            github=author['github'],
                            page=author['page'],
                        )                    
                        all_authors.append(remote_author)
            except Timeout:
                print("request timed out for", node.host)
                continue
            except ConnectionError:
                print("connection error for", node.host)
                continue

        serializer = ExploreUsersSerializer(all_authors, many=True, context={'author': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**swagger_docs["explore_authors_post"])
    def post(self, request: Request, uid: str) -> Response:
        """Determines relationship between current user and author

        Args:
            request (request): request containing the author ID
                authorID (str): ID of other author 

        Returns:
            response: a string response indicating the relation
        """
        authorID = request.data['authorID']
        user = get_object_or_404(Author, pk=uid)
        author = get_object_or_404(Author, pk=authorID)
        serializer = ExploreUsersSerializer(author, context={'author': user})
        response = serializer.data['relation']
        return Response(response, status=status.HTTP_200_OK)
    
