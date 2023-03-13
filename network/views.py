from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User,Post,Follow,Like
import json

def index(request):
    all = Post.objects.all().order_by("id").reverse()
    paginator = Paginator(all,10)
    pages = request.GET.get('page')
    items = paginator.get_page(pages)
    likes = Like.objects.all()
    liked = []
    try:
        for like in likes:
            if like.user.id == request.user.id:
                liked.append(like.post.id)
    except:
        liked = []
    return render(request, "network/index.html",{
        "items" : items,
        "liked" : liked
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


def newPost(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))
    

def profile(request,user_id):
    user = User.objects.get(pk=user_id)
    all = Post.objects.filter(user=user).order_by("id").reverse()

    followers = Follow.objects.filter(user=user)
    following = Follow.objects.filter(follower=user)

    try:
        check = followers.filter(follower=User.objects.get(pk=request.user.id))
        if len(check) != 0:
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    likes = Like.objects.all()
    liked = []
    try:
        for like in likes:
            if like.user.id == request.user.id:
                liked.append(like.post.id)
    except:
        liked = []
    paginator = Paginator(all,10)
    pages = request.GET.get('page')
    items = paginator.get_page(pages)
    return render(request, "network/profile.html",{
        "items" : items,
        "following" : following,
        "followers" : followers,
        "isFollowing" : isFollowing,
        "user_profile" : user,
        "liked" : liked
    })

def follow(request):
    follow = request.POST['followuser']
    current = User.objects.get(pk=request.user.id)
    data = User.objects.get(username=follow)
    f = Follow(follower=current,user=data)
    f.save()
    user_id = data.id
    return HttpResponseRedirect(reverse(profile,kwargs={"user_id":user_id}))

def unfollow(request):
    follow = request.POST['followuser']
    current = User.objects.get(pk=request.user.id)
    data = User.objects.get(username=follow)
    f = Follow.objects.get(follower=current,user=data)
    f.delete()
    user_id = data.id
    return HttpResponseRedirect(reverse(profile,kwargs={"user_id":user_id}))

def following(request):
    user = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(follower=user)
    all = Post.objects.all().order_by("id").reverse()
    posts = []
    for post in all:
        for person in following:
            if person.user == post.user:
                posts.append(post)
    likes = Like.objects.all()
    liked = []
    try:
        for like in likes:
            if like.user.id == request.user.id:
                liked.append(like.post.id)
    except:
        liked = []
    paginator = Paginator(posts,10)
    pages = request.GET.get('page')
    items = paginator.get_page(pages)
    return render(request, "network/following.html",{
        "items" : items,
        "liked" : liked
    })

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        post = Post.objects.get(pk=post_id)
        post.content = data["content"]
        post.save()
        return JsonResponse({"message": "Changed successfully", "data": data["content"]})


def unlike(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    num_likes = Like.objects.filter(post=post).count()
    return JsonResponse({"message": "Like removed","num_likes": num_likes})

def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like(user=user, post=post)
    like.save()
    num_likes = Like.objects.filter(post=post).count()
    return JsonResponse({"message": "Like added","num_likes": num_likes})


