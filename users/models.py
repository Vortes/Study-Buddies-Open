from django.db import models
from django.contrib.auth.models import User
from post.models import Post

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    participating_in = models.ForeignKey(
        Post, on_delete=models.SET_NULL, default=None, null=True
    )
    image = models.ImageField(default="default.png", upload_to="profile_pics")

    def __str__(self):
        return f"{ self.user }'s Profile"

