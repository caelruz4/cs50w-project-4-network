from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image_url = models.URLField(blank=True)
    bio = models.TextField(max_length=100, blank=True)
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # likes
    likes = models.ManyToManyField(User, related_name="post_like", blank=True)

    # count likes
    def likes_count(self):
        return self.likes.count()
    
    class Meta:
        ordering = ('-created_at', )
    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}...'

class Follower(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f'{self.follower.username} follows {self.following}'
    
# profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=100, blank=True, default="Hello, World!")
    def __str__(self):
        return f"{self.user.username} profile"
