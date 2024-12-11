
from rest_framework import serializers
from .models import Author, AuthorManager
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['type', 'id', 'uid', 'username', 'host', 'displayName', 'page', 'profileImage', 'github', 'biography']

#serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['email', 'username', 'password', 'displayName', 'github']  #specifying fields for user registration
        extra_kwargs = {'password': {'write_only': True}}  #ensuring password is write-only
    
    def create(self, validated_data):
        #create a new user with validated data
        user = Author.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            displayName=validated_data['displayName'],
            github=validated_data.get('github_username', ''),
        )
        user.set_password(validated_data['password'])  #hashing password

        user.id = f"{user.host}authors/{user.uid}"
        user.page = f"{user.host}authors/{user.uid}"

        user.save()  #saving user to database
        return user

#serializer for user login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  #field for username input
    password = serializers.CharField(write_only=True)  #password input, write-only
    access = serializers.CharField(read_only=True)  #field for JWT access token, read-only
    refresh = serializers.CharField(read_only=True)  #field for JWT refresh token, read-only

    def validate(self, data):
        username = data.get('username')  #retrieve username from input data
        password = data.get('password')  #retrieve password from input data
        
        # check if user has been created 
        user = get_user_model()
        try:
            user = Author.objects.get(username=username)
        except Author.DoesNotExist:
            raise serializers.ValidationError("Incorrect username")

        # check if user has been approved
        if not user.is_active:
            raise serializers.ValidationError("Account is awaiting approval")
        
        #authenticate user credentials
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid Credentials")  #raise error if credentials are invalid
        
        #generate JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)  #generate refresh token
        data['access'] = str(refresh.access_token)  #set access token in response
        data['refresh'] = str(refresh)  #set refresh token in response

        return {
            # return tokens and user info back to client
            'access': data['access'],  
            'refresh': data['refresh'],  
            'id': user.id, 
            'displayName': user.displayName, 
            'profileImage': user.profileImage,
            'github': user.github,  # Add github_username
            'biography': user.biography,
            'email': user.email,
        }

class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName', 'github', 'profileImage', 'page']