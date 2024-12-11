from rest_framework import serializers
from .models import Comment
from .models import Like
from authors.models import Author

#these classes define how the like and comment models should be serialised/deserialised


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["post", "author"]  

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['post', 'author', 'content', 'content_type', 'created_at', 'author_name'] 
    
