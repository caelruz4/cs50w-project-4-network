from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
# import messages
from django.contrib import messages
from django.db.models import Count

def index(request):
    posts = Post.objects.annotate(num_likes=Count('like')).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    post_on_page = paginator.get_page(page_number)

    liked_posts = Like.objects.filter(user=request.user, post__in=post_on_page).values_list('post', flat=True)
    liked_posts = Post.objects.filter(id__in=liked_posts)

    for post in post_on_page:
        post.is_liked = post in liked_posts

    context = {
        'posts': posts,
        'post_on_page': post_on_page,
    }
    return render(request, "network/index.html", context)

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


# post
@login_required
def post(request):
    if request.method == 'POST':
        post = Post(
            user=request.user,
            content=request.POST['content']
        )
        post.save()
        # message
        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))
# profile
@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    paginator = Paginator(posts, 10)
    # page number
    page_number = request.GET.get('page')
    is_current_user = request.user == user
    post_on_page = paginator.get_page(page_number)
    amount_of_posts = Post.objects.filter(user=user).count()
    # chech if i follow that user
    is_following = user.followers.filter(follower=request.user).exists()

    context = {
        'user': user,
        'posts': posts,
        'post_on_page': post_on_page,
        'current_user': is_current_user,
        'amount_of_posts': amount_of_posts,
        'is_following': is_following
    }
    return render(request, "network/profile.html", context)

# follow
@login_required
def follow(request, user_id):
    # if request post
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        if request.user != user:
            if user.followers.filter(follower=request.user).exists():
                # change to active
                user.followers.filter(follower=request.user).delete()
            else:
                user.followers.create(follower=request.user)

        return HttpResponseRedirect(reverse("profile", args=[user_id]))
    else:
        return HttpResponseRedirect(reverse("profile", args=[user_id]))
    
# my following
@login_required
def my_following(request):
    # select all following where follower is user
    following = Follower.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=following).order_by('-created_at')
    paginator = Paginator(posts, 10)
    # page number
    page_number = request.GET.get('page')
    post_on_page = paginator.get_page(page_number)
    following = True
    if len(posts) < 1:
        following = False
    context = {
        'posts': posts,
        'post_on_page': post_on_page,
        'my_following': True,
        'following': following
    }
    return render(request, "network/my-following.html", context)

def edit(request, post_id):
    if request.method == 'POST':
        new_content = request.POST.get('new_content', '')
        if new_content:
            post = Post.objects.get(id=post_id)
            post.content = new_content
            post.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

def toggle_like(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        user = request.user
        if Like.objects.filter(post=post, user=user).exists():
            Like.objects.filter(post=post, user=user).delete()
            liked = False
        else:
            Like.objects.create(post=post, user=user)
            liked = True

        total_likes = Like.objects.filter(post=post).count()

        return JsonResponse({'liked': liked, 'total_likes': total_likes})
    else:
        return JsonResponse({'error': 'Invalid request method'})