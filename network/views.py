from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
import random 

def user_is_authenticated(user):
    return user.is_authenticated

login_required_custom = user_passes_test(
    user_is_authenticated, login_url='login'
)

def index(request):
    # get every post 
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    post_on_page = paginator.get_page(page_number)

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
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            avatar =  create_avatar(first_name, last_name)
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name, image_url=avatar)
            user.save()

        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
def create_avatar(name, lastname):
    bgColors = ["c4b5fd", "fca5a5", "f9a8d4", "fde68a", "92C7CF"]
    fontColors= ["5b21b6", "dc2626", "db2777", "d97706", "075985"]
    index = random.randint(0, len(bgColors) - 1)
    return f'https://ui-avatars.com/api/?name={name}+{lastname}&rounded=true&size=128&background={bgColors[index]}&color={fontColors[index]}&bold=true'


@login_required_custom
def post(request):
    if request.method == 'POST':
        post = Post(
            user=request.user,
            content=request.POST['content']
        )
        post.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required_custom
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    is_current_user = request.user == user
    post_on_page = paginator.get_page(page_number)
    amount_of_posts = Post.objects.filter(user=user).count()
    is_following = user.followers.filter(follower=request.user).exists()

    context = {
        'user_profile': user,
        'posts': posts,
        'post_on_page': post_on_page,
        'current_user': is_current_user,
        'amount_of_posts': amount_of_posts,
        'is_following': is_following
    }
    return render(request, "network/profile.html", context)

@login_required_custom
def follow(request, user_id):
    if request.method == 'POST':
        user_profile = User.objects.get(id=user_id)
        if request.user != user_profile:
            if user_profile.followers.filter(follower=request.user).exists():
                user_profile.followers.filter(follower=request.user).delete()
            else:
                user_profile.followers.create(follower=request.user)

        return HttpResponseRedirect(reverse("profile", args=[user_id]))
    else:
        return HttpResponseRedirect(reverse("profile", args=[user_id]))
    
@login_required_custom
def my_following(request):
    following = Follower.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=following).order_by('-created_at')
    paginator = Paginator(posts, 10)
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

@login_required_custom

def edit(request, post_id):
    if request.method == 'POST':
        new_content = request.POST.get('new_content', '')
        if new_content:
            post = Post.objects.get(id=post_id)
            post.content = new_content
            post.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

# like
@login_required_custom

def toggle_like(request, post_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = get_object_or_404(Post, id=post_id)
            if post.likes.filter(id=request.user.id):
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True

            return JsonResponse({'liked': liked, 'likes_count': post.likes_count(), 'post_id': post_id })
        else:
            return redirect('login')
        
    return JsonResponse({'error': 'Invalid request or user not authenticated'})