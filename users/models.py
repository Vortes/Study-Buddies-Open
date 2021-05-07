from django.db import models
from django.contrib.auth.models import User
from post.models import Post


class FriendList(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    
    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
    
    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
    
    def unfriend(self, person_getting_unfriend):
        # user that is terminating friendship
        person_init_unfriend = self

        # remove person_getting_unfriend from person_init_unfriend's friend list
        person_init_unfriend.remove_friend(person_getting_unfriend)

        # remove person_init_unfriend from person_to_unfriend's friend list
        friends_list = FriendList.objects.get(user=person_getting_unfriend)
        friends_list.remove_friend(self.user)
    
    def is_mutual_friend(self, friend):

        # Check if person is a mutual of someone else
        if friend in self.friends.all():
            return True
        return False

    def __str__(self):
        return self.user.username


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username
    
    def accept(self):
        receiver_friend_list = FriendList.objects.get(user=self.receiver)

        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()
                print("reached save")
    
    def decline(self):
        self.is_active = False
        self.save()
    
    def cancel(self):
        self.is_active = False
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    friend_list = models.ForeignKey(FriendList, default=None, null=True, on_delete=models.CASCADE, related_name="friend_list")
    participating_in = models.ForeignKey(
        Post, on_delete=models.SET_NULL, default=None, null=True, related_name="participating_in"
    )
    image = models.ImageField(default="default.png", upload_to="profile_pics")

    def __str__(self):
        return f"{ self.user }'s Profile"