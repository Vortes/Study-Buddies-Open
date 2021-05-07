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

    # if current user is trying to access their own profile
    if request.user.is_authenticated and profile == request.user:
        return redirect("profile")
    # if current user is authenticated and they're not looking at own profile
    else:
        # Check to see if user is friend of current user
        if friends.filter(pk=request.user.id):
            is_friend = True
        else:
            is_friend = False
            
            print("data: ", get_friend_request_or_false(sender=request.user, receiver=profile))
            # CASE 1: Request has been sent from THEM to YOU
            if get_friend_request_or_false(sender=profile, receiver=request.user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                print("request_sent1: ", request_sent)
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=profile, receiver=request.user).id

            # CASE 2: Request has been sent from YOU to THEM
            elif get_friend_request_or_false(sender=request.user, receiver=profile) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                print("request_sent2: ", request_sent)

            # CASE 3: No request has been sent
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                print("request_sent3: ", request_sent)  


    response = ""
    other_user = get_presigned_url(profile)
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)

    context["profile"] = profile
    context["profile_image_url"] = response
    context["other_profile_url"] = other_user
    context["friends"] = friends 
    context["is_friend"] = is_friend 
    context["request_sent"] = request_sent
    context['id'] = profile.id

    return render(request, "users/public_profile.html", context)

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
            print("receiver: ", receiver)
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
