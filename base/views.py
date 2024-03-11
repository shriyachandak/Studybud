from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages #to use flash messages in the project
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required #this is the decorator used to restrict a user from performing a action without login
from django.db.models import Q #this is the Qlookup feature of django which help to search using different type of attributes like room name topic name or host
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm #this is django default registration form
from .models import Room, Topic, Messages
from .forms import RoomForm , UserForm
# rooms=[
#     {'id': 1, 'name':'Join Community For Python'},
#     {'id': 2, 'name':'This is all about C++'},
#     {'id': 3, 'name':'Grill up for CSS'}
# ]


def loginpage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, "user does not exist.")
        
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"username or password does not exist  ")

        
    context={'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerpage(request):
    page = 'register'
    form = UserCreationForm()
    if  request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit= False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration please try again')

    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html',context)

def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(desription__icontains=q)
        )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Messages.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms , 'topics': topics , 'room_count': room_count , 'room_messages':room_messages}
    return render(request,'base/home.html', context)

def room(request,pk):
    room = Room.objects.get(id = pk)
    room_messages = room.messages_set.all().order_by('-created')
    participants = room.participants.all() #.all is used for many to many and _set.all() is used to many to one relationships
    if request.method == 'POST':
        message = Messages.objects.create(
            user= request.user,
            room= room,
            body= request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room' : room, 'room_messages' : room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def user_profile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.messages_set.all()
    topics = Topic.objects.all()
    context={'user': user , 'rooms':rooms, 'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics= Topic.objects.all()
    if  request.method == 'POST':
        topic_name= request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name = topic_name)
        Room.objects.create(
            host= request.user,
            topic= topic,
            name= request.POST.get('name'),
            desription= request.POST.get('desription')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room= form.save(commit = False) 
        #     room.host = request.user
        #     room.save()
        return redirect('home') #redirecting to home page; imported above

    context={'form' : form, 'topics': topics}
    return render(request, 'base/room_create.html', context)

def update_room(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance = room) #instance is specified to show the previous value of the room
    topics= Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed !!')
    if request.method == 'POST':
        topic_name= request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name = topic_name)
        room.Topic= topic
        room.name= request.POST.get('name')
        room.desription= request.POST.get('desription')
        room.save()
        return redirect('home')
    context = {'form' : form ,'topics': topics , 'room':room}
    return render(request, 'base/room_create.html',context)
    
@login_required(login_url='login')
def delete_room(request,pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed !!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj': room})

@login_required(login_url='login')
def delete_message(request,pk):
    message = Messages.objects.get(id = pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed !!')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj': message})

@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance = user)
    if request.method == 'POST':
        form = UserForm(request.POST,instance = user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', pk = user.id)

    return render(request,'base/update_user.html',{'form': form})

def topics_page(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(Q(name__icontains=q))
    return render(request , 'base/topics.html',{'topics': topics})