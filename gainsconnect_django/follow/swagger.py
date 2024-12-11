from drf_yasg import openapi
from .serializers import *
from authors.serializers import SimpleAuthorSerializer
from rest_framework import status


swagger_docs = {
    "follow_request_post": {
        "operation_summary": "Create a new follow request",
        "operation_description": """
        Creates a follow request between two authors. Handles both local and remote follow requests.
        
        For remote requests, this endpoint will:
        1. Create a remote author object if it doesn't exist
        2. Forward the request to the remote server's inbox
        3. Create an immediate follower relationship for non-gainsconnect nodes
        """,
        "request_body": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['actor', 'object'],
            properties={
                'actor': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="The ID of the user sending the request"
                ),
                'object': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="The ID of the author receiving the request"
                        ),
                        'host': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="The host URL of the receiving author"
                        )
                    },
                    description="The author receiving the request"
                )
            }
        ),
        "responses": {
            201: openapi.Response(
                description="Follow request created successfully",
                examples={
                    "application/json": "request created"
                }
            ),
            400: openapi.Response(
                description="Invalid request data",
                examples={
                    "application/json": {
                        "actor": ["This field is required."],
                        "object": ["Invalid author data provided."]
                    }
                }
            ),
            500: openapi.Response(
                description="Error forwarding request to remote node",
                examples={
                    "application/json": "Failed to send request to remote node"
                }
            )
        }
    },
    "follow_request_get": {
        "operation_summary": "Retrieve follow requests for a specific author",
        "operation_description": """
        Returns a list of all authors who have sent follow requests to the specified author.
        The response includes basic information about each requesting author.
        """,
        "manual_parameters": [
            openapi.Parameter(
                "uid",
                openapi.IN_PATH,
                description="UUID of the author to retrieve follow requests for",
                type=openapi.TYPE_STRING,
                required=True,
                example="550e8400-e29b-41d4-a716-446655440000"
            )
        ],
        "responses": {
            200: openapi.Response(
                description="List of authors who have sent follow requests",
                examples={
                    "application/json": [
                        {
                            "id": "http://example.com/api/authors/123",
                            "displayName": "John Doe",
                            "profileImage": "http://example.com/profile.jpg",
                            "host": "http://example.com/",
                            "github": "http://github.com/johndoe",
                            "page": "http://example.com/authors/123"
                        }
                    ]
                }
            ),
            404: openapi.Response(
                description="Author not found",
                examples={
                    "application/json": "Author with specified UUID not found"
                }
            )
        }
    },
    "handle_request_post": {
        "operation_summary": "Accept or decline a follow request based on user's response",
        "operation_description": "Use this endpoint to respond to a follow request",
        "request_body": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['sender', 'receiver', 'reply'],
            properties={
                'sender': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the sender of the follow request"),
                'receiver': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the receiver (the current user)"),
                'reply': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Response to the follow request. `true` to accept, `false` to decline")
            }
        ),
        "responses": {
            status.HTTP_200_OK: openapi.Response(description="Success", examples={
                "application/json": "Request accepted"
            }),
            status.HTTP_200_OK: openapi.Response(description="Decline", examples={
                "application/json": "Decline request"
            }),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description="Invalid request"),
        }
    },
    "handle_request_put": {
        "operation_summary": "Accept a follow request and create follow relationship",
        "operation_description": """
        Accepts a follow request and creates a follow relationship between two authors.
        If the follower is remote, this endpoint will:
        1. Create the follow relationship
        2. Check and create friend relationship if bi-directional following exists
        3. Send all visible posts to the remote follower's inbox
        4. For remote followers, only non-friends-only posts are sent if the relationship is "Following"
        """,
        "manual_parameters": [
            openapi.Parameter(
                "uid",
                openapi.IN_PATH,
                description="UUID of the author accepting the follow request (followed)",
                type=openapi.TYPE_STRING,
                required=True,
                example="550e8400-e29b-41d4-a716-446655440000"
            ),
            openapi.Parameter(
                "fid",
                openapi.IN_PATH,
                description="ID of the author who sent the follow request (follower)",
                type=openapi.TYPE_STRING,
                required=True,
                example="http://example.com/api/authors/123"
            )
        ],
        "responses": {
            201: openapi.Response(
                description="Follow request accepted and relationship created",
                examples={
                    "application/json": "Request accepted"
                }
            ),
            404: openapi.Response(
                description="Author not found or follow request doesn't exist",
                examples={
                    "application/json": "Not found"
                }
            ),
            500: openapi.Response(
                description="Error sending posts to remote follower",
                examples={
                    "application/json": "Failed to send posts to follower {uid}: Connection refused"
                }
            )
        },
        "tags": ["follow"],
        "security": [
            {
                "Bearer": [],
                "Basic": []
            }
        ]
    },
    "handle_request_delete": {
        "operation_summary": "Unfollow an author",
        "operation_description": """
        Removes a follow relationship between two authors.
        If a friendship exists between the authors, it will also be removed.
        """,
        "manual_parameters": [
            openapi.Parameter(
                "uid",
                openapi.IN_PATH,
                description="UUID of the author who wants to unfollow (follower)",
                type=openapi.TYPE_STRING,
                required=True,
                example="550e8400-e29b-41d4-a716-446655440000"
            ),
            openapi.Parameter(
                "fid",
                openapi.IN_PATH,
                description="ID of the author being unfollowed (followed)",
                type=openapi.TYPE_STRING,
                required=True,
                example="http://example.com/api/authors/123"
            )
        ],
        "responses": {
            204: openapi.Response(
                description="Successfully unfollowed author",
                examples={
                    "application/json": "Unfollowed author"
                }
            ),
            404: openapi.Response(
                description="Author or follow relationship not found",
                examples={
                    "application/json": "Not found"
                }
            )
        }
    },
    "handle_request_get": {
        "operation_summary": "Check relationship between two authors",
        "operation_description": """
        Checks and returns the relationship status between two authors.
        Handles both local and remote author relationships.
        
        For remote authors:
        1. Queries the remote node for relationship status
        2. Updates local relationship records based on remote response
        3. Handles various scenarios like FOLLOWING -> FRIENDS transitions
        
        Possible relationship values:
        - "FOLLOWING": One-way follow relationship
        - "FRIENDS": Mutual follow relationship
        - "NONE": No relationship
        - "PENDING": Follow request exists but not accepted
        """,
        "manual_parameters": [
            openapi.Parameter(
                "uid",
                openapi.IN_PATH,
                description="UUID of the first author",
                type=openapi.TYPE_STRING,
                required=True,
                example="550e8400-e29b-41d4-a716-446655440000"
            ),
            openapi.Parameter(
                "fid",
                openapi.IN_PATH,
                description="ID of the second author",
                type=openapi.TYPE_STRING,
                required=True,
                example="http://example.com/api/authors/123"
            )
        ],
        "responses": {
            200: openapi.Response(
                description="Relationship status found",
                examples={
                    "application/json": "FRIENDS"  # or "FOLLOWING"
                }
            ),
            401: openapi.Response(
                description="Authorization header missing or invalid",
                examples={
                    "application/json": "Require Basic or Bearer authorization"
                }
            ),
            404: openapi.Response(
                description="No relationship exists or authors not found",
                examples={
                    "application/json": "NONE"  # or "PENDING"
                }
            ),
            408: openapi.Response(
                description="Remote server request timed out",
                examples={
                    "application/json": "Request timed out"
                }
            ),
            503: openapi.Response(
                description="Remote server connection error",
                examples={
                    "application/json": "Connection error"
                }
            )
        },
        "security": [
            {
                "Bearer": [],
                "Basic": []
            }
        ]
    },
    "list_follower_get": {
        "operation_summary": "Retrieve list of followers, following, or friends for a specific author",
        "operation_description": "Use this endpoint to retrieve a list of the author's followers, followings, or friends",
        "manual_parameters": [
            openapi.Parameter('id', openapi.IN_PATH, description="ID of the author", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('category', openapi.IN_PATH, description="The category of relationships to retrieve (`following`, `followed`, or `friends`)", type=openapi.TYPE_STRING, required=True),
        ],
        "responses": {
            status.HTTP_200_OK: openapi.Response(
                description="List of authors in the specified category",
                examples={
                    "application/json": [
                        {
                            "id": "1",
                            "display_name": "John Doe",
                            "profile_image": "http://example.com/profile.jpg"
                        },
                        {
                            "id": "2",
                            "display_name": "Jane Smith",
                            "profile_image": "http://example.com/profile2.jpg"
                        }
                    ]
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(description="Invalid category"),
        }
    },
    "explore_authors_get": {
        "operation_summary": "Retrieve a list of all other authors on the node and any other connected nodes for explore",
        "operation_description": "Use this endpoint to get all authors on the node except the current user",
        "manual_parameters": [
            openapi.Parameter('id', openapi.IN_PATH, description="ID of the author to exclude from the explore results", type=openapi.TYPE_STRING, required=True),
        ],
        "responses": {
            status.HTTP_200_OK: openapi.Response(
                description="List of authors excluding the specified author",
                examples={
                    "application/json": [
                        {
                            "id": "1",
                            "display_name": "Author One",
                            "profile_image": "http://example.com/profile1.jpg"
                        },
                        {
                            "id": "2",
                            "display_name": "Author Two",
                            "profile_image": "http://example.com/profile2.jpg"
                        }
                    ]
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="Author not found"),
        }
    },
    "explore_authors_post": {
        "operation_summary": "Determine and return the relationship between the current user and another author",
        "operation_description": "Use this endpoint to determine the relationship between two authors",
        "manual_parameters": [
            openapi.Parameter('id', openapi.IN_PATH, description="ID of the author initiating the relationship check", type=openapi.TYPE_STRING, required=True),
        ],
        "request_body": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'authorID': openapi.Schema(type=openapi.TYPE_STRING, description="ID of the target author to check the relationship with")
            },
            required=['authorID'],
        ),
        "responses": {
            status.HTTP_200_OK: openapi.Response(
                description="Relationship status between the two authors",
                examples={
                    "application/json": {
                        "relation": "following"
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="One or both authors not found"),
        }
    },
}