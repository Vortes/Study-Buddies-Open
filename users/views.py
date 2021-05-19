from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Profile, FriendList, FriendRequest
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User
from users.utils import get_friend_request_or_false
from users.friend_request_status import FriendRequestStatus
from post.models import Post
import boto3
import time
import json


def register(request):

    response = ''
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Signed in as {username}!")
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)
            return redirect("post-home")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form })


@login_required
def profile(request):
    try:
        friend_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True)
    except:
        pass

    # Get the friends of the profile you searched for
    try:
        friend_list = FriendList.objects.get(user=request.user)
    # if they dont have a friendlist, make a new one
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=request.user)
        friend_list.save()

    # Get number of friends
    friends = friend_list.friends.all()

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            time.sleep(3)
            messages.success(request, "Your account has been updated!")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    response = get_presigned_url(request.user)

    context = {
        "friends": friends,
        "u_form": u_form,
        "p_form": p_form,
        "profile_image_url": response,
        "friend_requests": friend_requests,
    }
    
    return render(request, "users/profile.html", context)


def public_profile(request, pk):
    context = {}
    profile = User.objects.get(pk=pk)
    is_friend = False
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

    # Get the friends of the profile you searched for
    try:
        friend_list = FriendList.objects.get(user=profile)
    # if they dont have a friendlist, make a new one
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=profile)
        friend_list.save()
    
    friends = friend_list.friends.all()
    
    if request.user.is_authenticated:
        # Get your friendlist
        try:
            friend_list_current_user = FriendList.objects.get(user=request.user)
        # if you dont have a friendlist, make a new one
        except FriendList.DoesNotExist:
            friend_list_current_user = FriendList(user=request.user)
            friend_list_current_user.save()


    # if current user is trying to access their own profile
    if request.user.is_authenticated and profile == request.user:
        return redirect("profile")
    # if current user is authenticated and they're not looking at own profile
    elif request.user.is_authenticated and profile != request.user:
        # Check to see if user is friend of current user
        if friends.filter(pk=request.user.id):
            is_friend = True
        else:
            is_friend = False
            
            # CASE 1: Request has been sent from THEM to YOU
            if get_friend_request_or_false(sender=profile, receiver=request.user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=profile, receiver=request.user).id

            # CASE 2: Request has been sent from YOU to THEM
            elif get_friend_request_or_false(sender=request.user, receiver=profile) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

            # CASE 3: No request has been sent
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value 


    response = ""
    other_user = get_presigned_url(profile)
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)
    
    participating_in = Profile.objects.get(user=profile).participating_in
    print(participating_in)

    context["post"] = participating_in
    context["participating_in"] = participating_in
    context["profile"] = profile
    context["profile_image_url"] = response
    context["other_profile_url"] = other_user
    context["friends"] = friends 
    context["is_friend"] = is_friend 
    context["request_sent"] = request_sent
    context['id'] = profile.id

    return render(request, "users/public_profile.html", context)   

@login_required()
def friend_list(request, *args, **kwargs):
    context = {}
    user = request.user
    user_id = kwargs.get("user_id")
    profile = User.objects.get(id=user_id)

    if user_id:

        if request.user.is_authenticated:
            # Get your friendlist
            try:
                friend_list_current_user = FriendList.objects.get(user=request.user)
            # if you dont have a friendlist, make a new one
            except FriendList.DoesNotExist:
                friend_list_current_user = FriendList(user=request.user)
                friend_list_current_user.save()

        try:
            this_user = User.objects.get(pk=user_id)
            context['this_user'] = this_user
        except User.DoesNotExist:
            return HttpResponse("That user does not exist")
        try:
            friend_list = FriendList.objects.get(user=this_user)
        except FriendList.DoesNotExist:
            return HttpResponse(f"could not find a friends list for {this_user.username}")
            

        friends = [] # [(account1, True), (account2, False)]
        auth_user_friend_list = FriendList.objects.get(user=user)

        for friend in friend_list.friends.all():
            friends.append((friend, auth_user_friend_list.is_mutual_friend(friend)))
        
        # get both recieved and sent friend requests
        friend_request_sent = [] 
        friend_request_received = []

        get_friend_requests_sent = FriendRequest.objects.filter(sender=request.user, is_active=True)
        get_friend_requests_received = FriendRequest.objects.filter(receiver=request.user, is_active=True)

        for friend_request in get_friend_requests_sent:
            friend_request_sent.append(friend_request.get_receiver())
        
        for friend_request in get_friend_requests_received:
            friend_request_received.append(friend_request.get_sender())
        

        context['friends'] = friends
        context['friend_request_sent'] = friend_request_sent
        context['friend_request_received'] = friend_request_received
        context['get_friend_request_sent'] = get_friend_requests_sent
        context['get_friend_request_received'] = get_friend_requests_received
        context['auth_user_friend_list'] = auth_user_friend_list
        context['profile'] = profile


        response = get_presigned_url(request.user)
        other_user = get_presigned_url(profile)

        context["other_user"] = other_user
        context["profile_image_url"] = response
    
    
    return render(request, "users/friend_list.html", context)


@login_required()
def list_friend_requests(request, pk):
    user = request.user
    profile = User.objects.get(pk=pk)

    if user == profile:
        friend_requests = FriendRequest.objects.filter(receiver=profile, is_active=True)
    else:
        return HttpResponse("You can't view another users friend requests.")
    
    response = ""
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)
    
    context = {
        "friend_requests": friend_requests,
        "profile_image_url": response,
    }

    return render(request, "users/friend_requests.html", context)
        

def send_friend_request(request):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = User.objects.get(id=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise Exception("Already sent friend request")
                    friend_requests = FriendRequest(sender=user, receiver=receiver)
                    friend_requests.save()
                    payload['response'] = "Friend request sent"

                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExist:
                friend_requests = FriendRequest(sender=user, receiver=receiver)
                friend_requests.save()
                payload['response'] = "Friend request sent"
            
            if payload['response'] == None:
                payload['response'] = "Something went wrong"
        else:
            payload['response'] = "Unable to send a friend request"
    else:
        payload['response'] = "You must be authenticated to send a friend request."
    
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required()
def accept_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "GET":
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            print("Hello", friend_request_id)
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm that is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request, now accept it
                    friend_request.accept()
                    payload['reponse'] = "Friend request accepted"
                else:
                    payload['response'] = "Something went wrong"
            else:
                payload['response'] = "That is not your request to accept"
        else:
            payload['response'] = "Unable to accept that friend request"
    
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required()
def decline_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "GET":
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm that is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request, now Decline it
                    friend_request.decline()
                    payload['reponse'] = "Friend request Declined"
                else:
                    payload['response'] = "Something went wrong"
            else:
                payload['response'] = "That is not your request to accept"
        else:
            payload['response'] = "Unable to accept that friend request"
    
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required()
def cancel_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST":
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            print("got receiver")
            receiver = User.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
            except Exception as e:
                payload['response'] = "Nothing to cancel. Friend request does not exist"
            
            # There should only ever be a single active friend request at any given time.
            # Cancel them all just in case

            if len(friend_requests) > 1:
                for request in friend_requests:
                    print("cancelling...")
                    request.cancel()
                    print("cancelled!")
                payload['response'] = "Friend request cancelled"
            else:
                # found the requst. Now cancel
                friend_requests.first().cancel()
                payload['response'] = "Friend request cancelled"
        else:
            payload['response'] = "Unable to cancel that friend request"
    
    return HttpResponse(json.dumps(payload), content_type="application/json")



@login_required()
def remove_friend(request, *args, **kwargs):
    user = request.user
    payload = {}

    if request.method == "POST":
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            try:
                removee = User.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['response'] = "Successfully removed that friend"
            except Exception as e:
                payload['response'] = f"Something went wrong: {str(e)}"
        else:
            payload['response'] = "Something went wrong"

    return HttpResponse(json.dumps(payload), content_type="application/json")


def get_presigned_url(user):

    # GET KEYS FROM SETTINGS
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME_RESIZED')
    region_name = getattr(settings, 'AWS_S3_REGION_NAME')
    aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
    aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID')

    # FETCH CURRENT USER PROFILE AND GET ITS PROFILE IMAGE
    current_profile = Profile.objects.filter(user=user)[0]

    key = ''
    profile_image_url = ''

    if current_profile:

        key = current_profile.image.name

        # GENERATE A PRESIGNED URL FOR REQUIRED PROFILE IMAGE
        client = boto3.client("s3", region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        try:
            profile_image_url = client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=3600)
        except ClientError as e:
            print("Unexpected error: %s" % e)

    return profile_image_url
