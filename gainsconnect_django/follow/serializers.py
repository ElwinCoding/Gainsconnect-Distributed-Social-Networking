from rest_framework import serializers
from .models import FollowRequest, Follower, Friends
from authors.models import Author
from authors.serializers import SimpleAuthorSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q


# serializer for follow requests
class FollowRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowRequest
        fields = ['type', 'summary', 'actor', 'object']

    def create(self, validated_data):
        # get the author objects
        actor = validated_data['actor']
        object = validated_data['object']
        summary = actor.displayName + " wants to follow " + object.displayName

        # create follow request
        follow_request = FollowRequest.objects.create(summary=summary, actor=actor, object=object)
        return follow_request
    
    # prevent from sending a follow request to oneself
    def validate(self, data):
        # prevent from sending a follow request to oneself
        if data['actor'] == data['object']:
            raise serializers.ValidationError("Actor and object cannot be the same.")
        return data

    def to_representation(self, instance):
        if isinstance(instance, dict):
            # Handle dictionary input
            return {
                'type': instance.get('type', 'follow'),
                'summary': instance.get('summary', ''),
                'actor': SimpleAuthorSerializer(instance['actor']).data,
                'object': SimpleAuthorSerializer(instance['object']).data
            }
        # Handle model instance
        return super().to_representation(instance)

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['follower', 'followed']

    def validate(self, data):
    # prevent from following oneself
        if data['follower'] == data['followed']:
            raise serializers.ValidationError("Follower and followed cannot be the same.")
        return data
    
class FollowListSerializer(serializers.Serializer):
    type = serializers.CharField(default="followers")
    followers = SimpleAuthorSerializer(many=True, read_only=True)

class ExploreUsersSerializer(serializers.ModelSerializer):
    relation = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'host', 'displayName', 'profileImage', 'page', 'github', 'relation']
    
    def get_relation(self, obj):
        '''
        Creates a field that specifies the author's relation to the user
        '''
        obj = Author.objects.filter(id=obj.id).first() or obj
        user = self.context['author']

        # check if the user is friends with this author
        friends = Friends.objects.filter(
            Q(author1=user) & Q(author2=obj) |
            Q(author1=obj) & Q(author2=user)
        ).exists()
    
        # check if the user follows this author
        follows = Follower.objects.filter(follower=user, followed=obj).exists()

        # check if the user has a pending follow request
        author_obj = Author.objects.filter(id=obj.id).first() or obj    
        follow_request = FollowRequest.objects.filter(actor=user, object=author_obj).exists()

        if friends:
            return 'FRIENDS'
        elif follows:
            return 'FOLLOWING'
        elif follow_request:
            return 'PENDING'
        else:
            return 'NONE'