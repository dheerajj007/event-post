from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Post, Topic, Message
from .forms import PostForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.contrib.admin.views.decorators import staff_member_required



def loginPage(request):
    page = 'login'

    # checking if user is already logged in 
    if request.user.is_authenticated:
        return redirect('home')

    # if user is sending some response
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)



def registerPage(request):
    form = UserCreationForm()
    context = {'form' : form}

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user  = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during regitration')

    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    # checking if it do have any parameters in it associated with q
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    posts = Post.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
 
    topics = Topic.objects.all()
    context = {'posts': posts, 'topics': topics}
    return render(request, 'base/home.html', context)


def post(request, pk):
    post = Post.objects.get(id=pk)
    post_messages = post.message_set.all().order_by('-created')

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            post = post,
            body = request.POST.get('body')
        )
        return redirect('post', pk=post.id)
    context = {'post': post, 'post_messages': post_messages}
    return render(request, 'base/post.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    posts = user.post_set.all()
    context = {'user': user, 'posts':posts}
    return render(request, 'base/profile.html', context)

# @login_required(login_url='login')
@staff_member_required()
def createPost(request):
    form = PostForm()
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/post_form.html', context)


@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)

    if request.user != post.creator:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
             
    context = {'form': form}
    return render(request, 'base/post_form.html', context)



@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)

    if request.user != post.creator:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        post.delete()
        return redirect('home')

    context = {'obj': post}
    return render(request, 'base/delete.html', context)



@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        message.delete()
        return redirect('home')

    context = {'obj': message}
    return render(request, 'base/delete.html', context)