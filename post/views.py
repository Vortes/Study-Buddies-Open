from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Post
from .forms import CreateForm
from users.models import Profile
from .filters import PostFilter
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
)
from django.conf import settings
from users.models import Profile
import boto3

def post_view(request):
    context = {}
    myFilter = PostFilter()

    posts = Post.objects.all()

    myFilter = PostFilter(request.GET, queryset=posts)
    posts = myFilter.qs

    response = ''

    if request.user.is_authenticated:
        response = get_presigned_url(request.user)

    context = {"posts": posts, "myFilter": myFilter, "profile_image_url": response}

    return render(request, "post/home.html", context)


class PostSearchResultView(ListView):
    model = Post
    template_name = "post/search_result.html"
    context_object_name = "search_results"
    ordering = ["-date_posted"]

    def get_queryset(self):
        query = self.request.GET.get("search")
        object_list = Post.objects.filter(
            Q(title__icontains=query) | Q(subject__tag_name__icontains=query) | Q(author__first_name__icontains=query)
        )
        return object_list


def detail_view(request, pk):

    participants = Profile.objects.all()

    join_button = request.POST.get("join_group")
    if join_button:
        if request.user.is_authenticated:
            profile = request.user.profile
            post_id = Post.objects.get(id=join_button)
            if profile.participating_in:
                messages.warning(
                    request,
                    f"You are currently in {profile.participating_in}, Please leave your group first",
                )
            elif post_id.num_participants >= post_id.max_buddies:
                messages.warning(request, "Sorry! This group is now full")
            else:
                profile.participating_in = post_id
                profile.save()
                post_id.num_participants += 1
                post_id.save()
                messages.success(
                    request,
                    f"Successfully joined {post_id}!",
                )
        else:
            messages.info(request, f"Please sign in or register first")
            return HttpResponseRedirect("/login")

    leave_button = request.POST.get("leave_group")
    if leave_button:
        profile = request.user.profile
        profile.participating_in = None
        profile.save()
        post_id2 = Post.objects.get(id=leave_button)
        post_id2.num_participants -= 1
        post_id2.save()
        messages.success(request, f"You have left {post_id2}")

    detail = Post.objects.get(pk=pk)
    response = ""
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)
    context = {"detail": detail, "participants": participants,  "profile_image_url": response }
    return render(request, "post/post_detail.html", context)


def create_view(request):
    context = {}

    form = CreateForm(request.POST)

    if request.user.profile.participating_in:
        group_id = request.user.profile.participating_in.id
        return HttpResponseRedirect(f"/post/{group_id}")
    else:
        if request.method == "POST":
            if form.is_valid():
                instance = form.save(commit=False)
                instance.author = request.user
                profile = instance.author.profile
                instance.save()
                post = Post.objects.get(title=instance.title)
                profile.participating_in = post
                profile.save()
                return HttpResponseRedirect(f"/post/{post.id}")

    response = get_presigned_url(request.user)

    context = {"form": form, "profile_image_url": response }

    return render(request, "post/post_form.html", context)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content", "subject", "max_buddies", "quiet_tag", "camera_tag"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        response = get_presigned_url(self.request.user)

        context['profile_image_url'] = response

        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        response = get_presigned_url(self.request.user)

        context['profile_image_url'] = response

        return context


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
        client = boto3.client("s3",region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        try:
            profile_image_url = client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=3600)
        except ClientError as e:
            print("Unexpected error: %s" % e)

    return profile_image_url
