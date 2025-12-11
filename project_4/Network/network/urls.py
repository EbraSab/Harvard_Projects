
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("new_post", views.new_post, name="new_post"),
    path("all_posts", views.index, name="all_posts"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("comments/<int:post_id>", views.comments, name="comments"),

    #API
    path('like_post/', views.like_post, name='like_post'),
    path('follow/', views.follow, name='follow'),
    path('edit_post/', views.edit_post, name='edit_post'),
    path('translate_content/', views.translate_content, name='translate_content'),
]
