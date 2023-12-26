import os
import random
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Room, Topic, Message ,User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import RoomForm, UserForm ,ProfileForm ,MyUserCreationForm
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login ,logout
from django.shortcuts import get_object_or_404
from django.http import JsonResponse



# ]
# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topic =Topic.objects.all()[0:5]
    #search
    rooms = Room.objects.filter(
        Q(topic__name__icontains =q) |
        Q(name__icontains = q)
    )
    
    room_count = rooms.count()
    room_message = Message.objects.filter(
        Q(room__topic__name__icontains =q))[0:3]
    all_users = User.objects.exclude(username = request.user.username)
    random_users = random.sample(list(all_users), min(2, len(all_users)))
    context = {'rooms':rooms,'topic':topic, 
               'room_count':room_count,'room_message':room_message ,'random_users':random_users,'users':all_users}

    return render(request,'base/home.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    # user_profile = Profile.objects.get(user=user)
    # img = user.profile.objects.proImg
    all_users = User.objects.exclude(username = request.user.username)
    random_users = random.sample(list(all_users), min(2, len(all_users)))
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topic = Topic.objects.all()[0:5]
    context ={'user':user,'rooms':rooms,'room_message':room_message,'topic':topic ,'random_users':random_users ,'users':all_users}
    return render(request,'base/profile.html',context)



def room(request,pk):
    room = Room.objects.get(id=pk)
    pa = room.participants.all()
    # print(participants)
    messages = room.message_set.all()
    # print(messages)

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body =request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context = {'rooms':room, 'message':messages, 'participants': pa}
    return render(request,'base/room.html',context)

def get_rooms(request, offset):
    # Lấy các phòng, ví dụ: 5 phòng mỗi lần tải
    rooms = Room.objects.all()[offset:offset + 5]
    data = {
        'html': render(request, 'room_partial.html', {'rooms': rooms}).content.decode('utf-8'),
        'has_more': len(rooms) == 5,  # Kiểm tra xem còn phòng để tải không
    }
    return JsonResponse(data)
#can dang nhap moi dung dc
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topic = Topic.objects.all()
    #kiem tra phuong thuc
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        Room.objects.create(
            host =request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
            password = request.POST.get('password'),
        )
        return redirect('home')
    context = {'form':form,"topic":topic}
    return render(request,'base/room_form.html',context)
    

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id= pk)
    form = RoomForm(instance=room)
    topic = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You fuck')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.password = request.POST.get('password')
        room.save()

        return redirect('home')

    context = {'form':form,'topic':topic,'room':room}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id = pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

def loginPage(request):

    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'')


        user = authenticate(request,username = username,password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else :
            messages.error(request,'wrong')

    context = {'page':page}
    return render(request,'base/login_sign.html',context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def sign(request):
    page = 'sign'
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user =form.save(commit = False)
            user.username = user.username.lower()
            user.save()
            login(request,user)

            # new_profile = Profile.objects.create(user=user)
            # new_profile.save()
            return redirect('home')
        else:
            messages.error(request,"sai")
        
    context = {'form':form}
    return render(request,'base/login_sign.html',context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form =UserForm(instance=user)
    context ={'form':form}
    if request.method =='POST':
        form =UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile',pk =user.id)
    return render(request,'base/update-user.html',context)


@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id = pk)
    # message = get_object_or_404(Message, id=pk)
    if request.user != message.user:
        return HttpResponse("this is not your comment")
    if request.method == 'POST':
        message.delete()
        return redirect('room',pk=message.room.id)
    return render(request,'base/delete.html',{'obj':message})




#upload img
@login_required(login_url='login')
def update_avatar(request):
    user = request.user
    form =ProfileForm(instance=user)
    context ={'form':form}
    if request.method =='POST':
        form =ProfileForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile',pk =user.id)
    return render(request,'base/upload_profile_image.html',context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains = q)
    return render(request,'base/topics.html',{'topics':topics})

def friendPages(request):
    current_user = request.user
    user = User.objects.exclude(username=current_user.username)
    return render(request,'base/allFriend.html',{'user':user})


def activityPages(request):
    room_message = Message.objects.all()
    return render(request,'base/activityvp.html',{})