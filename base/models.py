from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True )
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True )
    name = models.CharField(max_length=200) #CharField is use for limited text
    desription = models.TextField(null=True, blank=True)  #textfield is used for large text; no need to specify the max len of text 
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created'] #"-" is used to reverse the order to decending based on recently updated
    

    def __str__(self):
        return self.name

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated','-created'] #"-" is used to reverse the order to decending based on recently updated
            
    def __str__(self):
        return self.body[0:50]

