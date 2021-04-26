from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Message(models.Model):
    firstName = models.CharField(max_length=255)
    postPk = models.IntegerField()
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, default=None, null=True
    )

    class Meta:
        ordering = ('tag_name',)


    def __str__(self):
        return self.tag_name


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=(500))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    subject = models.ForeignKey(Tag, on_delete=models.SET_NULL, default=None, null=True)
    num_participants = models.IntegerField(default=1)

    class MaxGroupSize(models.IntegerChoices):
        small = 5, "Small 1-5"
        medium = 10, "Medium 1-10"
        large = 20, "Large 1-20"

    max_buddies = models.IntegerField(choices=MaxGroupSize.choices)

    quiet_tag = models.BooleanField("Group Muted")
    camera_tag = models.BooleanField("Group Camera Off")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})
