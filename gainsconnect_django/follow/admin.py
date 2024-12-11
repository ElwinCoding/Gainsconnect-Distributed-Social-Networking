from django.contrib import admin
from .models import Follower, FollowRequest, Friends

# Register your models here.
admin.site.register(Follower)
admin.site.register(FollowRequest)
admin.site.register(Friends)

