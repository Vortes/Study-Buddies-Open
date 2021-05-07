from django.contrib import admin
from .models import Profile, FriendList, FriendRequest

admin.site.register(Profile)
admin.site.register(FriendList)
admin.site.register(FriendRequest)
