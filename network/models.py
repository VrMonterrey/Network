from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.TextField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%m/%d/%Y, %H:%M:%S')}"
    
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")
    def __str__(self):
        return f"{self.follower} follows {self.user}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liking")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked")
    def __str__(self):
        return f"{self.user} liked {self.post}"