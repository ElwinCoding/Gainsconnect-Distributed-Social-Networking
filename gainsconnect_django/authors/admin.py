from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['id', 'uid', 'username', 'email', 'displayName', 'host', 'page', 'joined', 'is_active', 'is_staff']
    
    # Fields to make searchable
    search_fields = ['username', 'email', 'displayName']
    
    # Fields to filter by
    list_filter = ['is_active', 'is_remote', 'is_staff', 'joined']
    
    # Read-only fields
    readonly_fields = ['id', 'uid', 'joined', 'host', 'page']

    # Optional: Order by a specific field
    ordering = ['-joined']  # Orders by newest joined first

    # All fields that should be shown in the edit form
    fieldsets = [
        (None, {
            'fields': ['username', 'email', 'displayName', 'is_active', 'is_staff', 'is_remote']
        }),
        ('Profile Info', {
            'fields': ['profileImage', 'github', 'host', 'page']
        }),
        ('Important dates', {
            'fields': ['joined', 'id', 'uid']
        }),
    ]

