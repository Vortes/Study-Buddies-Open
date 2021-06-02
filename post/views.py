from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Message
from .forms import CreateForm
from .filters import PostFilter
from users.models import Profile
from django.conf import settings
import boto3
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
)


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home')

    all_posts = Post.objects.all().count()
    recent_posts = 0

    if all_posts >= 3:
        enough_posts = True
        recent_posts = Post.objects.all().order_by('-id')[:3]
    else:
        enough_posts = False

    context = {"recent_posts": recent_posts, "enough_posts": enough_posts}
    return render(request, "post/info-home.html", context)


def post_view(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    context = {}
    myFilter = PostFilter()

    posts = Post.objects.all()

    myFilter = PostFilter(request.GET, queryset=posts)
    posts = myFilter.qs

    general_group = Post.objects.filter(
        Q(subject__tag_name__icontains="A General Discussion Group")
    ).order_by('-date_posted')[:10]

    math_sciences_group = Post.objects.filter(
        Q(subject__category__category_name__icontains= "Maths & Sciences")
    ).order_by('-date_posted')[:10]

    arts_humanities_group = Post.objects.filter(
        Q(subject__category__category_name__icontains="Arts & Humanities")
    ).order_by('-date_posted')[:10]

    computing_group = Post.objects.filter(
        Q(subject__category__category_name__icontains="Computing")
    ).order_by('-date_posted')[:10]

    economics_group = Post.objects.filter(
        Q(subject__category__category_name__icontains="Economics")
    ).order_by('-date_posted')[:10]

    test_prep_group = Post.objects.filter(
        Q(subject__category__category_name__icontains="Test Prep")
    ).order_by('-date_posted')[:10]

    response = ''

    if request.user.is_authenticated:
        response = get_presigned_url(request.user)

    print(general_group)
    print(math_sciences_group)

    context = {
                "posts": posts, 
                "myFilter": myFilter, 
                "profile_image_url": response, 
                "general_group": general_group,
                "math_sciences_group": math_sciences_group,
                "arts_humanities_group": arts_humanities_group,
                "computing_group": computing_group,
                "economics_group": economics_group,
                "test_prep_group": test_prep_group,
               }

    return render(request, "post/home.html", context)


def search_view(request):

    query = request.GET.get("search")
    post_query = Post.objects.filter(
        Q(title__icontains=query) | Q(subject__tag_name__icontains=query)
    )
    num_of_posts = len(post_query)
    print("posts: ", num_of_posts)

    response = ""
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)

    context = {
        "posts": post_query,
        "profile_image_url": response,
        "query": query,
        "num_of_posts": num_of_posts,
    }

    search_user_clicked = request.POST.get("search_user")

    if search_user_clicked:
        user_query = User.objects.filter(
            Q(username__icontains=query)| Q(first_name__icontains=query)
        )
        num_of_users = len(user_query)
        context["users"] = user_query
        context["num_of_users"] = num_of_users

        return render(request, "post/search_users.html", context)
    
    return render(request, "post/search_posts.html", context)


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
            messages.warning(request, f"Please sign in or register first")
            return HttpResponseRedirect(reverse('login'))

    leave_button = request.POST.get("leave_group")
    if leave_button:
        profile = request.user.profile
        profile.participating_in = None
        profile.save()
        post_id2 = Post.objects.get(id=leave_button)
        post_id2.num_participants -= 1
        post_id2.save()
        messages.success(request, f"You have left {post_id2}")

    chats = Message.objects.filter(postPk=pk)[0:25]
    detail = Post.objects.get(pk=pk)
    response = ""
    if request.user.is_authenticated:
        response = get_presigned_url(request.user)
    context = {"detail": detail, "participants": participants, "profile_image_url": response, "chats":chats, "pk":pk,}
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