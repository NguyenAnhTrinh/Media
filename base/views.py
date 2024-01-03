import os
import random
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Room, Topic, Message ,User , Friendship
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
    current_user = request.user
    #search
    rooms = Room.objects.filter(
        Q(topic__name__icontains =q) |
        Q(name__icontains = q)
    )
    sent = Friendship.objects.filter(receiver=request.user, status='pending')
    room_count = rooms.count()
    room_message = Message.objects.filter(
        Q(room__topic__name__icontains =q))[0:5]
    

    accepted_friends = Friendship.objects.filter(Q(sender=request.user, status='accepted') | Q(receiver=request.user, status='accepted'))


    all_users = User.objects.exclude(
        Q(id=current_user.id) |
        Q(friendship_sent__receiver=current_user, friendship_sent__status='accepted') |
        Q(friendship_received__sender=current_user, friendship_received__status='accepted') |
        Q(friendship_sent__sender=current_user, friendship_sent__status='pending')
    ).exclude(
        Q(friendship_sent__receiver=current_user, friendship_sent__status='pending') |
        Q(friendship_received__sender=current_user, friendship_received__status='pending')
    ).exclude(
        Q(friendship_sent__receiver=current_user, friendship_sent__status='accepted') |
        Q(friendship_received__sender=current_user, friendship_received__status='accepted')
    ).filter(username__icontains=q)
    
    random_users = random.sample(list(all_users), min(4, len(all_users)))
    context = {'rooms':rooms,'topic':topic, 
               'room_count':room_count,'room_message':room_message ,'random_users':random_users,'users':accepted_friends,'sent':sent}

    return render(request,'base/home.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    # user_profile = Profile.objects.get(user=user)
    # img = user.profile.objects.proImg

    friendship = Friendship.objects.filter(
        Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
    ).first()
    #hien thi cac request for addfr
    sent = Friendship.objects.filter(receiver=request.user, status='pending')


    #cac ban be trong trang thai da accepted
    accepted_friends = Friendship.objects.filter(Q(sender=request.user, status='accepted') | Q(receiver=request.user, status='accepted'))


    #cac ban be thuoc chua request va da reject
    all_users = User.objects.exclude(
    Q(id=request.user.id) | 
    Q(friendship_sent__receiver=request.user, friendship_sent__status='accepted') | 
    Q(friendship_received__sender=request.user, friendship_received__status='accepted') | 
    Q(friendship_sent__receiver=request.user, friendship_sent__status='rejected') | 
    Q(friendship_received__sender=request.user, friendship_received__status='rejected')
    )
    random_users = random.sample(list(all_users), min(5, len(all_users)))
    rooms = user.room_set.all()
    room_message = user.message_set.all()[0:5]
    topic = Topic.objects.all()[0:5]
    context ={'user':user,'rooms':rooms,
              'room_message':room_message,
              'topic':topic ,
              'random_users':random_users ,
              'users':accepted_friends,
              'sent':sent,
              'friendship':friendship,}
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
            # password = request.POST.get('password'),
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
    return redirect('login')


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
    q = request.GET.get('q', '')
    current_user = request.user
    users = User.objects.exclude(id=current_user.id).filter(username__icontains=q)

    friendships_sent = Friendship.objects.filter(sender=current_user, status='pending')
    sent_friend_requests = [friendship.receiver for friendship in friendships_sent]

    friendships_received = Friendship.objects.filter(receiver=current_user, status='pending')
    received_friend_requests = [friendship.sender for friendship in friendships_received]

    friendships_accepted = Friendship.objects.filter(Q(sender=current_user, status='accepted') | Q(receiver=current_user, status='accepted'))
    accepted_friends = [friendship.sender if friendship.receiver == current_user else friendship.receiver for friendship in friendships_accepted]

    return render(request, 'base/allFriend.html', {
        'users': users,
        'current_user': current_user,
        'sent_friend_requests': sent_friend_requests,
        'received_friend_requests': received_friend_requests,
        'accepted_friends': accepted_friends,
    })

def myFriends(request):
    q = request.GET.get('q', '')  # Use an empty string as default if 'q' is not present
    current_user = request.user

    # Filter friends based on search query and friendship status
    user = Friendship.objects.filter(
        (Q(sender=current_user, status='accepted') | Q(receiver=current_user, status='accepted'))
        & (Q(sender__username__icontains=q) | Q(receiver__username__icontains=q))
    )
    return render(request,'base/myfriend.html',{'user':user})

def activityPages(request):
    room_message = Message.objects.all()
    return render(request,'base/activityvp.html',{})





#add friend
def sentRequest(request,pk):
    receiver = get_object_or_404(User, pk=pk)

    # Check if there is any previous friendship request (including rejected ones)
    previous_request = Friendship.objects.filter(sender=request.user, receiver=receiver).first()

    if previous_request:
        # If there is a previous request, resend it
        previous_request.status = 'pending'
        previous_request.save()
        messages.success(request, 'Friend request resent successfully.')
    else:
        # If there is no previous request, create a new one
        Friendship.objects.create(sender=request.user, receiver=receiver, status='pending')
        messages.success(request, 'Friend request sent successfully.')

    return redirect('profile', pk=pk)

def acceptRequest(request,pk):
    sender = User.objects.get(pk=pk)

        # Check if there is a pending friend request
    friendship_request = Friendship.objects.filter(sender=sender, receiver=request.user, status='pending').first()

    if friendship_request:
        friendship_request.status = 'accepted'
        friendship_request.save()
        messages.success(request, f'You are now friends with {sender.username}.')
    else:
        messages.warning(request, 'No pending friend request found.')

    return redirect('profile', pk=pk)


def reject(request, pk):
    sender = get_object_or_404(User, pk=pk)

    friendship_request = Friendship.objects.filter(
        (Q(sender=sender, receiver=request.user) | Q(sender=request.user, receiver=sender)),
        status__in=['pending', 'accepted']
    ).first()

    if friendship_request:
        # If the status is 'accepted', update it to 'rejected'
        if friendship_request.status == 'accepted':
            friendship_request.status = 'rejected'
            friendship_request.save()
            messages.success(request, f'Friendship with {sender.username} rejected.')
        # If the status is 'pending', delete the friend request
        elif friendship_request.status == 'pending':
            friendship_request.delete()
            messages.success(request, f'Friend request from {sender.username} rejected.')
    else:
        messages.warning(request, 'No pending or accepted friend request found with this user.')

    return redirect('profile', pk=pk)
