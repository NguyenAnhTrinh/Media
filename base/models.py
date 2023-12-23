from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE )
    proImg = models.ImageField(upload_to='profile_images/',default='defaut1.png',null=True)

    def __str__(seft):
        return seft.user.username
    



class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(seft):
        return seft.name
# Create your models here.
class Room(models.Model):
    host = models.ForeignKey(User,on_delete=models.SET_NULL,null =True)
    topic = models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null = True, blank = True)
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    password = models.TextField(null = True, blank = True)
    

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
    

    
    