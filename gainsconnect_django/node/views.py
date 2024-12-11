from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from .models import AuthNode
import base64

class NodeUser:
    is_authenticated = True

class NodeAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for nodes using Basic Authentication.
    """
    def authenticate(self, request):
        print("received request in node authentication")
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # If request is for JWT token, skip authentication
        if auth_header.startswith('Bearer '):
            return None

        if not auth_header or not auth_header.startswith('Basic '):
            raise exceptions.AuthenticationFailed('Authentication required')
            
        try:
            # Decode Basic auth credentials
            auth = auth_header.split(' ')[1]
            decoded = base64.b64decode(auth).decode('utf-8')
            username, password = decoded.split(':')
            verified = False

            # Verify agaisnt default credentials
            if username == settings.BASIC_AUTH_USERNAME and password == settings.BASIC_AUTH_PASSWORD:
                print("Verified using default credentials")
                verified = True

            # Verify agaisnt AuthNode table
            auth_node = AuthNode.objects.filter(username=username, password=password).first()
            if auth_node and not auth_node.is_blocked:
                print("Verified using AuthNode table", auth_node.name)
                verified = True
            
            if verified:
                print("=== Method 1: META HTTP Headers ===")
                for key, value in request.META.items():
                    if key.startswith('HTTP_'):
                        print(f"{key}: {value}")

                return (NodeUser(), None)
            else:
                raise exceptions.AuthenticationFailed('Invalid username and/or password')

        except (IndexError, ValueError, UnicodeDecodeError):
            raise exceptions.AuthenticationFailed('Invalid basic auth header')

    def authenticate_header(self, request):
        """
        Only return Basic auth header if there's no Bearer token
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return 'Basic realm="Node Authentication"'
        return None
