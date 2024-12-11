from drf_yasg import openapi
from .serializers import *

swagger_docs = {
    "repost_post" : {
        'operation_summary': "Reposts a public post",
        'operation_description': "Creates a post object of the original post that is being shared",
        'request_body': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['original_post_id'],
            properties={
                'original_post_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the original post')
            }
        ),
        'examples': [
            {
                "description": "Successful repost of an existing post",
                "value": {"original_post_id": "post456"},
                "response": {
                    "status": 200,
                    "data": {
                        "id": "repost789",
                        "title": "Repost of Exciting News!",
                        "author": {"id": "user123", "display_name": "ReposterUser"},
                        "original_post": {"id": "post456", "title": "Exciting News!", "author": {"id": "author456", "display_name": "OriginalAuthor"}},
                        "created_at": "2024-02-15T12:00:00Z",
                        "visibility": "unlisted"
                    }
                }
            },
            {
                "description": "Error: Missing `original_post_id`",
                "value": {"original_post_id": ""},
                "response": {
                    "status": 400,
                    "data": {"error": "Bad Request - `original_post_id` is missing or invalid."}
                }
            }
        ],
        'responses': {
            200: PostSerializer,
            400: "Bad Request - Missing or invalid `original_post_id`."
        },
    },
    "delete_post": {
        "operation_summary": "Soft-delete a specific post",
        "operation_description": """
        ### `DELETE /api/posts/{post_id}/delete/`
        - **Purpose**: Soft-deletes a post by marking it as deleted.
        - **When to Use**: When a user wants to delete their post.
        - **Why to Use**: Allows users to remove unwanted posts while keeping a record.
        """,
        'examples' : [{
            "description": "Example 1 - Successfully deleting a post",
            "value": {
                "method": "DELETE",
                "url": "/api/posts/123/delete/",
                "expected_response": {
                    "status": 204,
                    "description": "No Content - Post with ID 123 successfully deleted."
                }
            }
        },
        {
            "description": "Example 2 - Attempt to delete a post that does not exist",
            "value": {
                "method": "DELETE",
                "url": "/api/posts/999/delete/",
                "expected_response": {
                    "status": 404,
                    "description": "Not Found - Post with ID 999 does not exist."
                }
            }
        },
        {
            "description": "Example 3 - Unauthorized attempt to delete another user's post",
            "value": {
                "method": "DELETE",
                "url": "/api/posts/123/delete/",
                "expected_response": {
                    "status": 403,
                    "description": "Forbidden - User does not have permission to delete post with ID 123."
                }
            }
        }],
        "manual_parameters": [
            openapi.Parameter('post_id', openapi.IN_PATH, description="ID of the post to delete", type=openapi.TYPE_STRING)
        ],
        "responses": {
            204: "No Content - Post successfully deleted",
            404: "Not Found - Post not found",
            403: "Forbidden - User not authorized to delete this post",
        },
    },
    "post_list_get": {
        "operation_summary": "Retrieve a list of posts",
        "operation_description": """
        ### `GET /api/posts/`
        - **Purpose**: Retrieves a list of all posts.
        - **When to Use**: To fetch all posts available on the platform.
        - **Why to Use**: Useful for displaying a feed of posts to users.
        """,
        "examples" : [
            {
                "description": "Example Response - Public and friends-only posts",
                "value": {
                    "status": 200,
                    "data": [
                        {
                            "id": "1",
                            "title": "Exploring the Mountains",
                            "content": "A beautiful journey through the mountains",
                            "visibility": "public",
                            "author": {"id": "author123", "display_name": "JohnDoe"},
                            "created_at": "2024-01-15T12:00:00Z",
                            "updated_at": "2024-01-15T12:00:00Z",
                            "likesCount": 15
                        },
                        {
                            "id": "2",
                            "title": "My Private Thoughts",
                            "content": "Reflections on life",
                            "visibility": "friends",
                            "author": {"id": "author124", "display_name": "JaneSmith"},
                            "created_at": "2024-02-01T08:45:00Z",
                            "updated_at": "2024-02-01T08:45:00Z",
                            "likesCount": 8
                        }
                    ]
                }
            },
            {
                "description": "Example Response - No posts available",
                "value": {
                    "status": 200,
                    "data": []
                }
            }
        ],
        "responses": {
            200: openapi.Response(description="List of posts", schema=PostSerializer(many=True)),
        },
    },
    "post_list_post": {
        "operation_summary": "Create a new post",
        "operation_description": """
        ### `POST /api/posts/`
        - **Purpose**: Creates a new post.
        - **When to Use**: To allow users to create a new post.
        - **Why to Use**: Enables content creation by users.
        """,
        "request_body": PostSerializer,
        "examples": [
            {
                "description": "Example Request - Public post creation",
                "value": {
                    "title": "A Day in the Life",
                    "content": "Sharing the experiences of my day.",
                    "visibility": "public"
                },
                "response": {
                    "status": 201,
                    "data": {
                        "id": "3",
                        "title": "A Day in the Life",
                        "content": "Sharing the experiences of my day.",
                        "visibility": "public",
                        "author": {"id": "author123", "display_name": "JohnDoe"},
                        "created_at": "2024-03-01T10:00:00Z",
                        "updated_at": "2024-03-01T10:00:00Z",
                        "likesCount": 0
                    }
                }
            },
            {
                "description": "Example Request - Friends-only post creation",
                "value": {
                    "title": "Personal Reflections",
                    "content": "Some thoughts I'd like to share with friends only.",
                    "visibility": "friends"
                },
                "response": {
                    "status": 201,
                    "data": {
                        "id": "4",
                        "title": "Personal Reflections",
                        "content": "Some thoughts I'd like to share with friends only.",
                        "visibility": "friends",
                        "author": {"id": "author124", "display_name": "JaneSmith"},
                        "created_at": "2024-03-05T09:30:00Z",
                        "updated_at": "2024-03-05T09:30:00Z",
                        "likesCount": 0
                    }
                }
            },
            {
                "description": "Example Request - Validation error",
                "value": {
                    "title": "",
                    "content": "This post lacks a title."
                },
                "response": {
                    "status": 400,
                    "data": {
                        "detail": "Validation error: title field is required."
                    }
                }
            }
        ],
        "responses": {
            201: openapi.Response(description="Created post", schema=PostSerializer),
            400: "Bad Request - Validation errors in the request data",
        },
    },
    "edit_post": {
        "operation_summary": "Edit an existing post",
        "operation_description": """
        ### `PUT /api/posts/{post_id}/edit/`
        - **Purpose**: Updates the details of a specified post.
        - **When to Use**: When a user wants to modify their post content.
        - **Why to Use**: Allows users to update their posts.
        """,
        "request_body": PostSerializer,
        "examples": [
            {
                "description": "Update post title and content",
                "value": {
                    "title": "Updated Title",
                    "content": "This is the updated content of the post."
                }
            },
            {
                "description": "Change visibility to unlisted",
                "value": {
                    "visibility": "unlisted"
                }
            }
        ],
        "manual_parameters": [
            openapi.Parameter('post_id', openapi.IN_PATH, description="ID of the post to edit", type=openapi.TYPE_STRING)
        ],
        "responses": {
            200: PostSerializer,
            404: "Not Found - Post not found",
            400: "Bad Request - Validation errors",
        },
    },
    "profile_posts_view": {
        "operation_summary": "Retrieve posts from an author's profile",
        "operation_description": """
        ### `GET /posts/profile-posts/`
        - **Purpose**: Retrieves a stream of posts of an author's profile.
        - **When to Use**: For displaying a user's profile with public posts.
        - **Why to Use**: Enhances user experience by showing content from author's profile page.
        """,
        "examples": [
            {
                "description": "Public posts for another user's profile",
                "value": {"author_id": "author456"},
                "response": {
                    "status": 200,
                    "data": [
                        {
                            "id": "post3",
                            "title": "Welcome to My Profile",
                            "visibility": "public",
                            "author": {"id": "author456", "display_name": "Author456"},
                            "created_at": "2024-01-18T08:00:00Z"
                        }
                    ]
                }
            },
            {
                "description": "Retrieve all posts for logged-in user's profile",
                "value": {"author_id": "author123"},
                "response": {
                    "status": 200,
                    "data": [
                        {
                            "id": "post1",
                            "title": "My Private Post",
                            "visibility": "private",
                            "author": {"id": "author123", "display_name": "AuthorName"},
                            "created_at": "2024-01-15T10:00:00Z"
                        },
                        {
                            "id": "post2",
                            "title": "Public Post on My Profile",
                            "visibility": "public",
                            "author": {"id": "author123", "display_name": "AuthorName"},
                            "created_at": "2024-01-20T10:00:00Z"
                        }
                    ]
                }
            },
            {
                "description": "No posts found",
                "value": {"author_id": "nonexistent_author"},
                "response": {
                    "status": 404,
                    "data": {"error": "No posts found for this author"}
                }
            }
        ],
        "responses": {
            200: openapi.Response(description="List of profile posts", schema=PostSerializer(many=True))
        },
    },
    "stream_view": {
        "operation_summary": "Retrieve personalized stream of posts",
        "operation_description": """
        ### `GET /posts/stream/`
        - **Purpose**: Retrieves a personalized stream of posts.
        - **When to Use**: For displaying a user's feed with relevant posts.
        - **Why to Use**: Enhances user experience by showing content from followed authors.
        """,
        "examples": [
            {
                "description": "Personalized post stream for logged-in user",
                "value": {},
                "response": {
                    "status": 200,
                    "data": [
                        {
                            "id": "post123",
                            "title": "Public Post",
                            "visibility": "public",
                            "author": {"id": "author1", "display_name": "Author One"},
                            "created_at": "2024-03-01T10:00:00Z"
                        },
                        {
                            "id": "post456",
                            "title": "Friends-Only Post",
                            "visibility": "friends",
                            "author": {"id": "author2", "display_name": "Author Two"},
                            "created_at": "2024-03-02T14:30:00Z"
                        }
                    ]
                }
            },
            {
                "description": "No posts available",
                "value": {},
                "response": {
                    "status": 200,
                    "data": []
                }
            }
        ],
        "responses": {
            200: openapi.Response(description="Personalized stream of posts", schema=PostSerializer(many=True))
        },
    },
    "post_detail_view": {
        "operation_summary": "Retrieve details of a specific post",
        "operation_description": """
        ### `GET /api/posts/{id}/`
        - **Purpose**: Provides details for a specific post by ID.
        - **When to Use**: To view the full content of a single post.
        - **Why to Use**: Useful for detailed post views.
        """,
        "manual_parameters": [
            openapi.Parameter('id', openapi.IN_PATH, description="Unique identifier of the post", type=openapi.TYPE_STRING)
        ],
        "examples": [
            {
                "description": "Retrieve specific post by ID 'post123'",
                "value": {"id": "post123"},
                "response": {
                    "status": 200,
                    "data": {
                        "id": "post123",
                        "title": "My First Post",
                        "author": {"id": "author789", "display_name": "AuthorName"},
                        "created_at": "2024-01-01T12:00:00Z",
                        "visibility": "public"
                    }
                }
            },
            {
                "description": "Post not found",
                "value": {"id": "nonexistentpost"},
                "response": {
                    "status": 404,
                    "data": {"detail": "Post does not exist."}
                }
            }
        ],
        "responses": {
            200: PostSerializer,
            404: "Not Found - Post does not exist."
        },
    },
}