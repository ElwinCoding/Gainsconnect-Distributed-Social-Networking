from drf_yasg import openapi
from rest_framework import status

swagger_docs = {
    "get_github_usernames": {
        "operation_summary": "Retrieve GitHub Usernames",
        "operation_description": "This endpoint returns a list of GitHub usernames for all authors.",
        "responses": {
            200: openapi.Response(
                description="A list of GitHub usernames.",
                examples={
                    "application/json": {
                        "usernames": ["john_doe", "jane_smith", "dev_user"]
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request"
            )
        }
    }
}
