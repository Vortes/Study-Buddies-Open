from django.urls import path
from . import views
from .views import (
    PostUpdateView,
    PostDeleteView,
    search_view,
    # SearchUserView,
)

urlpatterns = [
    path("", views.home_view, name="post-info"),
    path("home/", views.post_view, name="post-home"),
    path("post/<int:pk>/", views.detail_view, name="post-detail"),
    path("post/<int:pk>/update/", PostUpdateView.as_view(), name="post-update"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"),
    path("post/create/", views.create_view, name="post-create"),
    path("post/search_result/posts",search_view, name="search-post-results"),
]
