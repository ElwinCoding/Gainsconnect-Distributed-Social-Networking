from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from follow.models import *
from follow.serializers import *
from posts.models import *
from comments.models import *
from comments.serializers import *
from authors.models import *
from authors.serializers import *
from posts.models import *
from comments.models import *
from node.views import NodeAuthentication
from posts.models import *
from posts.serializers import *
from uuid import uuid4
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime
from urllib.parse import urlparse
from django.utils.timezone import now



class InboxView(APIView):
    authentication_classes = [NodeAuthentication]
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, uid):
        print("received", uid)
        # print("type", request.data)

        if request.data['type'] == 'follow':
            return self.handleFollow(request, uid)

        if request.data['type'] == 'comment':
            return self.handleComment(request, uid)

        if request.data['type'] == 'like':
            return self.handleLike(request, uid)
        
        if request.data['type'] == 'post':
            return self.handlePost(request, uid)
        
        if request.data['type'] == 'posts':
            return self.handlePosts(request, uid)


        return Response("Inbox", status=status.HTTP_200_OK)


    def handleFollow(self, request, uid):
        print("handle follow")
        print("request body", request.data)
        object = get_object_or_404(Author, pk=uid)
        actor_data = request.data['actor']

        # check if actor exists, create if not
        try:
            actor = Author.objects.get(id=actor_data['id'])
            print("got actor", actor)
        except Author.DoesNotExist:
            actor = Author.objects.create_remote_author(actor_data)
            print("created actor:", actor.displayName, "with id", actor.id)

        # Check if already following
        if Follower.objects.filter(follower=actor, followed=object).exists():
            return Response("Already following this author", status=status.HTTP_400_BAD_REQUEST)

        # Check if follow request already exists
        if FollowRequest.objects.filter(actor=actor, object=object).exists():
            return Response("Follow request already exists", status=status.HTTP_400_BAD_REQUEST)
        
        # create follow request
        follow_request = FollowRequest.objects.create(
            actor = actor,
            object = object,
        )
        print("follow request created")
        return Response("Follow request created", status=status.HTTP_200_OK)
    
    def handleComment(self, request, uid):
        print("handle comment", uid)
        print("request", request)

        """
        Parses an incoming comment object and adds it to the database.
        """
        if request.content_type != 'application/json':
            return Response({'detail': 'Content-Type must be application/json'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the comment data from the request
        comment_data = request.data
        
        # Fetch or create the author of the comment
        author_data = comment_data['author']
        print('33333333333')
        print(comment_data)
        print('766666666667777')
        print(author_data)
        print('777777777777777')
        print(uid)
       
        try:
            print("this is before")
            author = Author.objects.get(uid=uid)
            print("this is after")

        except Author.DoesNotExist:
            author = Author.objects.create_remote_author(author_data)
        print('779999999977')
        print(author)
        # Ensure the target object exists 
        target_object_url = comment_data['post']
        parsed_url = urlparse(target_object_url)
        target_object_url_uuid = parsed_url.path.split('/')[-1]
        print(target_object_url)
        print(target_object_url_uuid)

        target_object = None
        try:
            # Check if the target is a Post
            print("this is before@@@@", target_object_url_uuid)
            
            print("post id is:", target_object_url)
            print("all post ids and names are:")
    
            # Query all Post objects and print their names and ids
            all_posts = Post.objects.all()
            
            for post in all_posts:
                id_of_post = urlparse(post.id).path.split('/')[-1]
                print(f"Post UID: {post.uid}, POST NAME: {post.title}, POST ID FROM URL: {id_of_post}, POST URL: {post.id}")
    
            
            target_object = Post.objects.get(id=target_object_url)
            
            print("this is after@@@@")

        except Post.DoesNotExist:
            return Response({"error": "Target object not found"}, status=status.HTTP_404_NOT_FOUND)

        print("try except block finished")
        print(author.displayName)
        print(author_data['displayName'])

        # Create the comment
        print(author)
        comment = Comment.objects.create(
            author=author,
            post=target_object,
            created_at=comment_data.get('published', now()),
            content=comment_data.get('comment'),
            content_type=comment_data.get('contentType', 'text/plain'),
            author_name=author_data['displayName']
        )
        print("comment object finished creating")
        
        #Construct the comment_data response in the required format
        # response_comment_data = {
        #     "type": "comment",
        #     "author": {
        #         "type": "author",
        #         "id": "http://nodeaaaa/api/authors/111",
        #         "page": "http://nodeaaaa/authors/greg",
        #         "host": "http://nodeaaaa/api/",
        #         "displayName": "Greg Johnson",
        #         "github": "http://github.com/gjohnson",
        #         "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
        #     },
        #     "comment": comment.content,
        #     "contentType": comment.content_type,
        #     "published": comment.created_at.isoformat(),
        #     "id": f"{target_object_url}/comments/{comment.id}",
        #     "post": target_object.id,
        # }

        #print("Response comment data:", response_comment_data)
        print("DONE receiving")

        return Response({"message": "Comment created"}, status=status.HTTP_200_OK)


    def handleLike(self, request, uid):
        print("handle like", uid)

        # Validate the author (receiver of the like)
       # object = get_object_or_404(Author, pk=uid)

        # Extract the like data from the request
        like_data = request.data
        print ("AKAKAKA")
        if 'author' not in like_data or 'object' not in like_data:
            return Response({"error": "Missing required fields in 'like' object"}, status=status.HTTP_400_BAD_REQUEST)
        print("is this printing???")
        
        # Fetch or create the author of the like
        author_data = like_data['author']

        try:
            print("this is before")
            author = Author.objects.get(uid=uid)
            print("this is after")

        except Author.DoesNotExist:
            author = Author.objects.create_remote_author(author_data)

        # Ensure the target object exists (post or comment)
        target_object_url = like_data['object']
        parsed_url = urlparse(target_object_url)
        target_object_url_uuid = parsed_url.path.split('/')[-1]

        target_object = None
        try:
            # Check if the target is a Post
            print("post id is:", target_object_url_uuid)
    
            # Query all Post objects and print their names and ids
            all_posts = Post.objects.all()
            
            for post in all_posts:
                id_of_post = urlparse(post.id).path.split('/')[-1]            
                print(f"Post UID: {post.uid}, POST NAME: {post.title}, POST ID FROM URL: {id_of_post}, POST URL: {post.id}")

            
            target_object = Post.objects.get(id=target_object_url)            
            print("post id is:", target_object_url_uuid)

        except Post.DoesNotExist:
            try:
                # Check if the target is a Comment
                target_object = Comment.objects.get(id=target_object_url)
            except Comment.DoesNotExist:
                return Response({"error": "Target object not found"}, status=status.HTTP_404_NOT_FOUND)

        print("try except block finished")

        # Check for duplicate likes
        # if Like.objects.filter(author=author, post=target_object).exists():
        #      print("Duplicate like detected, skipping creation.")
        #      return Response({"message": "Duplicate like ignored"}, status=status.HTTP_200_OK)
        
        # Create and save the like
        like = Like.objects.create(
            author=author,
            post=target_object if isinstance(target_object, Post) else None,
            created_at=like_data.get('published', timezone.now()),
        )

        print("like object finished creating")
        print("DONE receiving")
        return Response({"message": "Like created"}, status=status.HTTP_200_OK)

    def handlePost(self, request, uid, post_data=None):
        print("handle post", uid)
        print("request", request.data)

        if post_data is None:
            post_data = request.data

        author_data = post_data.get('author', {})
        print("author data", author_data)
        author_id_url = author_data.get('id')
        print("author id url", author_id_url)

        # Ensure the URL is not empty
        if not author_id_url:
            print("Error: Author ID URL is empty")
            return Response({"error": "Invalid author ID URL"}, status=status.HTTP_400_BAD_REQUEST)

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

        post_id = post_data.get('id')
        print("post id", post_id)

        try: 
            post = Post.objects.get(id=post_id)

            if post_data.get('visibility') == 'DELETED':
                post.is_deleted = True
                post.visibility = 'DELETED'
                post.save()
                return Response("Post was deleted", status=status.HTTP_200_OK)
            
            post.title = post_data.get('title', post.title)
            post.description = post_data.get('description', post.description)
            post.content = post_data.get('content', post.content)
            post.visibility = post_data.get('visibility', post.visibility)
            post.save()
            return Response("Post updated successfully", status=status.HTTP_200_OK)
        
        except Post.DoesNotExist:
            serializer = PostSerializer(data=post_data, context={'author':author})
            if serializer.is_valid():
                try:
                    post = serializer.save()
                    print("Post created successfully: ", post)
                    return Response("Post created", status=status.HTTP_200_OK)
                except Exception as e:
                    print("AN error occurred while creating the post: ", e)
                    return Response({"error": "Failed to create post"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print("Validation errors:", serializer.errors)
                return  Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def handlePosts(self, request, uid):
        print("handle posts", uid)
        print("request", request)

        # Ensure the request content type is JSON
        if request.content_type != 'application/json':
            return Response({'detail': 'Content-Type must be application/json'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the list of posts from the request data
        posts_data = request.data.get('items', [])
        print("this is the posts_data", posts_data)
        if not posts_data:
            return Response({'detail': 'No posts data provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Process each post in the list
        for post_data in posts_data:
            print("this is the post_data", post_data)
            response = self.handlePost(None, uid, post_data)
            print("response", response)
            if response.status_code != status.HTTP_200_OK:
                print("Error processing post:", response.data)
                return Response({"error": "Failed to process post"}, status=response.status_code)

        return Response("Posts processed", status=status.HTTP_200_OK)
    