from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Profile
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User
import boto3
import time

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
        "profile_image_url": response
    }
    
    return render(request, "users/profile.html", context)

def public_profile(request, pk):
    profile = User.objects.get(pk=pk)
    
    add_friend_button = request.POST.get("add_friend")
    if add_friend_button:
        pass


    response = ""
    other_user = get_presigned_url(profile)
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)

    context = {"profile": profile, "profile_image_url": response, "other_profile_url": other_user}

    return render(request, "users/public_profile.html", context)


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
