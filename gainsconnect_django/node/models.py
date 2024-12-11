from django.db import models

# Create your models here.
class Node(models.Model):
    host = models.URLField(max_length=200)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class AuthNode(models.Model):
    host = models.URLField(max_length=200)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name