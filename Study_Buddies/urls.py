from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("post.urls"), name="post-home"),
    path("secretaccessadmin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("register/", user_views.register, name="register"),
    path("profile/", user_views.profile, name="profile"),
    path("profile/<int:pk>/", user_views.public_profile, name="public-profile"),
    path('profile/friend_remove/', user_views.remove_friend, name="remove-friend"),
    path('profile/friend_request/', user_views.send_friend_request, name="friend-request"),
    path('profile/friend_request/<int:pk>/', user_views.list_friend_requests, name="list-friend-requests"),
    path('profile/accept_friend_request/<friend_request_id>/', user_views.accept_friend_request, name="accept-friend-request"),
    path('profile/decline_friend_request/<friend_request_id>/', user_views.decline_friend_request, name="decline-friend-request"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
