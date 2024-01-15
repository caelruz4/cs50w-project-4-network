from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

def index(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 10)
    # page number
    page_number = request.GET.get('page')
    post_on_page = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'post_on_page': post_on_page
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
@csrf_exempt  # Asegúrate de usar csrf_exempt para permitir solicitudes POST sin CSRF
@login_required
def post(request):
    if request.method == "POST":
        user = request.user
        content = request.POST["content"]
        post = Post(user=user, content=content)
        post.save()
        # get all data of new comment
        data = {
            "id": post.id,
            "content": post.content,
            "user": post.user.username,
            "created_at": post.created_at
        }
        return JsonResponse({'success': True, 'content': data})
    else:
        return render(request, "network/index.html")


# profile
@login_required
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    paginator = Paginator(posts, 10)
    # page number
    page_number = request.GET.get('page')
    post_on_page = paginator.get_page(page_number)
    context = {
        'user': user,
        'posts': posts,
        'post_on_page': post_on_page
    }
    return render(request, "network/profile.html", context)