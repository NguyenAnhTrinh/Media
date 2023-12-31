import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length = 200, null = True)
    email =models.EmailField(unique = True,null =True)
    bio = models.TextField(null = True)

    avatar = models.ImageField(default='defaut1.png',null=True)

    USERNAME_FIELD ='email'
    REQUIRED_FIELDS = []



class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(seft):
        return seft.name
# Create your models here.
class Room(models.Model):
    # id = models.UUIDField(primary_key= True, default =uuid.uuid4)
    host = models.ForeignKey(User,on_delete=models.SET_NULL,null =True)
    topic = models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=200,null =True)
    img = models.ImageField(default='',null=True)
    description = models.TextField(null = True, blank = True)
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','created']

    def __str__(seft):
        return seft.name
    
class Message(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated','created']
    def __str__(seft):
        return seft.body[0:50]
    



#friend
class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_received')
    status = models.CharField(max_length=20, default='pending')  # 'pending', 'accepted', 'rejected'

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username} ({self.status})"
    
