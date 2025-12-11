from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from translate import Translator

from .models import User, Post, Comment


def index(request):
    posts = Post.objects.order_by("-post_date")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html",{
        "posts": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url="login")
def new_post(request):
    if request.method == "POST":

        data = request.POST

        Post.objects.create(
            content=data["content"],
            user=request.user
        )

        return redirect("index")

    return redirect("index")


def profile(request, user_id):
    user_profile = get_object_or_404(User, pk=user_id)
    posts = Post.objects.filter(user=user_profile).order_by("-post_date")
    paginator = Paginator(posts,10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html",{
        "posts": page_obj,
        "followers": user_profile.followers.all(),
        "following": user_profile.following.all(),
        "username": user_profile.username,
        "user_id": user_profile.id
    })


@login_required
def following(request):
    
    following = request.user.following.all()
    posts = Post.objects.filter(user__in=following).order_by("-post_date")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "posts": page_obj 
    })


def comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)

    if request.method == "POST":
        data = request.POST
        Comment.objects.create(
            com_content=data["content"],
            user=request.user,
            post=post
        )
        return redirect('comments', post_id=post_id)

    return render(request, "network/comments.html", {
        "comments": comments.order_by("-com_date"),
        "post": post
    })


def translate_content(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    text = request.POST.get('text', '').strip()
    target_lang = request.POST.get('lang', '').strip()

    if not text or not target_lang:
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    try:
        translator = Translator(to_lang=target_lang)
        translation = translator.translate(text)
        return JsonResponse({"translation": translation})
    except Exception as e:
        return JsonResponse({"error": f"Translation failed: {str(e)}"}, status=500)


@login_required
def like_post(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        'likes_count': post.likes.count(),
        'liked': liked,
        'post_id': post.id,
    })


@login_required
def follow(request):
    user_to_follow_id = request.POST.get('user_id')
    user_to_follow = get_object_or_404(User, id=user_to_follow_id)
    current_user = request.user

    if user_to_follow in current_user.following.all():
        current_user.following.remove(user_to_follow)
        following = False
    else:
        current_user.following.add(user_to_follow)
        following = True

    # Get updated counts
    followers_count = user_to_follow.followers.count()
    following_count = current_user.following.count()

    return JsonResponse({
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@login_required
def edit_post(request):
    post_id = request.POST.get('post_id')
    new_content = request.POST.get('content')
    post = get_object_or_404(Post, id=post_id)

    # Only post owner can edit
    if post.user != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    post.content = new_content
    post.save()

    return JsonResponse({
        'post_id': post.id,
        'content': post.content,
    })

