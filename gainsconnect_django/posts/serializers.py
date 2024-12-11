from rest_framework import serializers
from .models import Post
from comments.serializers import CommentSerializer, LikeSerializer
import base64
import os
from authors.serializers import SimpleAuthorSerializer

class PostSerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    #original_post_data = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, write_only=True)
    visibility = serializers.CharField(required=False)
    content = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Post
        fields = ['uid', 'id', 'author', 'title', 'description', 
                  'content', 'contentType', 'visibility', 
                  'published', 'updated_at', 'comments', 
                  'likes', 'image']
        read_only_fields = ['author']

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.get_absolute_url())
    
    def get_original_post_data(self, obj):
        if obj.original_post:
            if obj.original_post.is_deleted:
                return "deleted"
            else:
                return PostSerializer(obj.original_post, context=self.context).data

    def get_content(self, obj):
        return obj.get_content()

    def create(self, validated_data):
        print("this is the validated_data ", validated_data)

        # Create post instance
        try:
            image = None
            if 'request' in self.context:
                image = self.context['request'].FILES.get('image')
                print("image", image)

            print("creating")
            post = Post(**validated_data)
            print("could create")
        
            # Handle image if present
            if image:
                print("Processing image") 
                # Read the file content and encode it
                image_content = image.read()
                base64_image = base64.b64encode(image_content).decode('utf-8')
                # Store the base64 string
                post.content = base64_image

                # in case user set wrong content type
                if image.content_type == 'image/jpeg':
                    post.contentType = 'image/jpeg;base64'
                elif image.content_type == 'image/png':
                    post.contentType = 'image/png;base64'
                
            post.save()
            return post
        except Exception as e:
            print("Error creating Post:", e)
            raise

    def validate(self, attrs):
        print("attrs in validation", attrs)
        attrs = super().validate(attrs)
        
        # Get author from context
        author = self.context.get('author')
        if not author:
            raise serializers.ValidationError("Author is required in context")
        

        validated_data = attrs.copy()
        validated_data.pop('image', None)
        validated_data['author'] = author


        # check if image exists
        is_local_upload = 'request' in self.context and self.context['request'].FILES.get('image')

        # Only set content to empty string if it's an image upload
        if attrs.get('contentType') in ['image/jpeg;base64', 'image/png;base64']:
            if is_local_upload:
                validated_data['content'] = ''
            else:
                validated_data['content'] = attrs.get('content', '')
        else:
            validated_data['content'] = attrs.get('content', '')
            
        print("validated_data in validation", validated_data)

        return validated_data

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        if image:
            # Read the file content and encode it
            image_content = image.read()
            base64_image = base64.b64encode(image_content).decode('utf-8')
            # Store the base64 string
            instance.content = base64_image

            # in case user set wrong content type
            if image.content_type == 'image/jpeg':
                instance.contentType = 'image/jpeg;base64'
            elif image.content_type == 'image/png':
                instance.contentType = 'image/png;base64'
            
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
    
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Modify the content field based on content_type
        if instance.contentType.startswith('text/'):
            # If it's text, return the content as is
            representation['content'] = instance.content
        else:
            # If it's an image, format it as a data URL
            representation['content'] = f"data:{instance.contentType},{instance.content}"
        
        return representation
    
    def get_comments(self, obj):
        comments_data = CommentSerializer(obj.comment_post.all(), many=True).data
        return {
            "type": "comments",
            "page": obj.id,
            "id": obj.id + "/comments",
            "page_number": 1,
            "size": 10,
            "count": len(comments_data),
            "src": comments_data
        }
    
    def get_likes(self, obj):
        likes_data = LikeSerializer(obj.like_post.all(), many=True).data
        return {
            "type": "likes",
            "page": obj.id,
            "id": obj.id + "/likes",
            "page_number": 1,
            "size": 10,
            "count": len(likes_data),
            "src": likes_data
        }