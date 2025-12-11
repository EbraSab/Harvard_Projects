from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True
    )



class Post(models.Model):

    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)



class Comment(models.Model):

    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    com_content = models.TextField()
    com_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name="comment", on_delete=models.CASCADE, null=True)
