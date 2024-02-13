import os
import random
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Room, Topic, Message ,User , Friendship ,Chat ,Product,Order,OrderDetail, Cart , CartItem , Event,Invitation,Store
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import RoomForm, UserForm ,ProfileForm ,MyUserCreationForm,EventsForm,StoreForm,ProductForm,CheckoutForm
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login ,logout
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.db import transaction



# ]
# Create your views here.

#Home Page
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

#End Homepage


#Authenticate and Profile
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
    Q(friendship_sent__receiver=request.user, friendship_sent__status='pending') | 
    Q(friendship_received__sender=request.user, friendship_received__status='pending')
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


#End profile

#Room Function

def room(request,pk):
    room = Room.objects.get(id=pk)
    pa = room.participants.all()
    # print(participants)
    messages = room.message_set.all()
    # print(messages)
    if request.user == room.host or room.is_private==False or request.user in pa:
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

    if room.is_private and request.user not in pa:
        if request.method == 'POST' and 'answer' in request.POST:
            user_answer = request.POST.get('answer', '').strip().lower()
            correct_answer = room.answer.lower()
            if correct_answer in user_answer:
                room.participants.add(request.user)
                # Redirect sau khi trả lời đúng có thể đưa người dùng vào trang của phòng
                return redirect('room', pk=room.id)
            else:
                # messages.error(request, "Câu trả lời không đúng. Bạn không thể vào phòng này.")
                # Chuyển hướng người dùng về trang khác hoặc hiển thị form trả lời lại
                return redirect('home')  # Thay thế 'some-view' bằng view hoặc URL thích hợp

        # Hiển thị form trả lời cho người dùng nếu là GET request hoặc câu trả lời sai
        return render(request, 'base/room_question.html', {'room': room})

    



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
            is_private = request.POST.get('is_private'),
            question = request.POST.get('question'),
            answer = request.POST.get('answer'),

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
        return HttpResponse('')
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



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains = q)
    return render(request,'base/topics.html',{'topics':topics})

#FriendShip Function

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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def acceptRequest(request,pk):
    sender = User.objects.get(pk=pk)

        # Check if there is a pending friend request
    friendship_request = Friendship.objects.filter(Q(sender=sender, receiver=request.user, status='pending')|Q(sender=request.user, receiver=sender, status='pending')).first()

    if friendship_request:
        friendship_request.status = 'accepted'
        friendship_request.save()
        messages.success(request, f'You are now friends with {sender.username}.')
    else:
        messages.warning(request, 'No pending friend request found.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def reject(request, pk):
    sender = get_object_or_404(User, pk=pk)

    friendship_request = Friendship.objects.filter(
        (Q(sender=sender, receiver=request.user) | Q(sender=request.user, receiver=sender)),
        status__in=['pending', 'accepted']
    ).first()

    if friendship_request:
        # If the status is 'accepted', update it to 'rejected'
        if friendship_request.status == 'accepted':
            friendship_request.delete()
            messages.success(request, f'Friendship with {sender.username} rejected.')
        # If the status is 'pending', delete the friend request
        elif friendship_request.status == 'pending':
            friendship_request.delete()
            messages.success(request, f'Friend request from {sender.username} rejected.')
    else:
        messages.warning(request, 'No pending or accepted friend request found with this user.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#Chat with Friend function
def chat(request):
    query = request.GET.get('q', '')  # Lấy tham số tìm kiếm từ request.GET
    # Bắt đầu với tất cả bạn bè đã chấp nhận
    accepted_friends = Friendship.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        status='accepted'
    )
    # Nếu có từ khóa tìm kiếm, lọc kết quả dựa trên từ khóa đó
    if query:
        accepted_friends = accepted_friends.filter(
            Q(sender__username__icontains=query) | 
            Q(receiver__username__icontains=query)
        )
    context ={'accepted_friends':accepted_friends}

    return render(request,'base/chat.html',context)

@login_required
def open_chat(request, pk):
    friend = User.objects.get(id=pk)
    messages = Chat.objects.filter(
        (Q(sender=request.user, receiver=friend) | Q(sender=friend, receiver=request.user))
    )
    accepted_friends = Friendship.objects.filter(Q(sender=request.user, status='accepted') | Q(receiver=request.user, status='accepted'))

    if request.method == 'POST':
        chat = Chat.objects.create(
            sender = request.user,
            receiver = friend,
            content =request.POST.get('body'),
        )
        # room.participants.add(request.user)
        return redirect('open_chat',pk=pk)
    return render(request, 'base/chat.html', {'friend': friend, 'messages': messages,'accepted_friends':accepted_friends})

def delete_message_chat(request, message_id):
    message = get_object_or_404(Chat, id=message_id)

    # Check if the user has permission to delete the message
    if request.user == message.sender:
        message.delete()
        messages.success(request, 'Message deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this message.')

    # Redirect back to the chat room or any other appropriate page
    return redirect('open_chat', pk=message.receiver.id)


#End chat function

# shop ban hang
#done
def shopping (request):
    # products = Product.objects.all()
    q = request.GET.get('q', '')
    # Lấy store của người dùng hiện tại
    
    # Tìm kiếm sản phẩm trong store của người dùng hiện tại
    products = Product.objects.filter(
        Q(description__icontains=q) | 
        Q(name__icontains=q)
    )
    user_store = Store.objects.filter(owner=request.user)
    # Tìm kiếm cửa hàng của người dùng hiện tại
    stores = user_store.filter(
        Q(name__icontains=q)
    )
    context = {'products': products, 'stores': stores}
    return render(request, 'base/store.html', context)

#done
@login_required
def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('shop')
    else:
        form = StoreForm()
    return render(request, 'base/store_form.html', {'form': form})







@login_required
def update_store(request, pk):
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('shop')
    else:
        form = StoreForm(instance=store)
    return render(request, 'base/store_form.html', {'form': form, 'store': store})



@login_required
def delete_store(request, pk):
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == 'POST':
        store.delete()
        return redirect('shop')
    return render(request, 'base/delete.html', {'store': store})


def store_detail(request,pk):
    store = get_object_or_404(Store, id=pk)
    products = Product.objects.filter(store=store)
    stores = Store.objects.filter(owner=request.user)
    # Tìm kiếm cửa hàng của người dùng hiện tại

    context = {'store':store, 'products':products ,'stores':stores}
    return render(request,'base/store_profile_detail.html',context)



def store_products(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    query = request.GET.get('q')
    stores = Store.objects.filter(owner=request.user)

    if query:
        # Lọc sản phẩm dựa trên từ khóa tìm kiếm trong tên hoặc mô tả sản phẩm
        products = Product.objects.filter(
            Q(store=store),
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.filter(store=store)

    return render(request, 'base/store_detail.html', {'store': store, 'products': products,'stores':stores})



@login_required
def product_create(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('store_products', store_id=store.id)
    else:
        form = ProductForm()
    return render(request, 'base/product_form.html', {'form': form, 'store': store})

@login_required
def product_update(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store_products', store_id=store.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'base/product_form.html', {'form': form, 'store': store})

@login_required
def product_delete(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        product.delete()
        return redirect('store_products', store_id=store.id)
    return render(request, 'base/product_delete.html', {'product': product, 'store': store})



def product_detail(request, store_id, product_id):
    stores = Store.objects.filter(owner=request.user)

    product = get_object_or_404(Product, store__id=store_id, id=product_id)
    return render(request, 'base/product_detail.html', {'product': product,'stores':stores})





@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)

    # Lấy số lượng từ form, sử dụng giá trị mặc định là 1 nếu không tìm thấy
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        cart=cart,
    )
    if not created:
        # Cập nhật số lượng dựa trên giá trị nhập vào từ form
        cart_item.quantity += quantity
    else:
        # Nếu là lần đầu tiên sản phẩm được thêm vào giỏ, thiết lập số lượng
        cart_item.quantity = quantity
    cart_item.save()

    # Redirect to the previous page or cart detail page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))





def cart_detail(request):
    stores = Store.objects.filter(owner=request.user)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        total_price = cart.get_total_price()
    else:
        items = []
        total_price = 0

    context = {
        'cart_items': items,
        'total_price': total_price,
        'stores':stores,
    }
    return render(request, 'base/cart_detail.html', context)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    # Quay trở lại trang giỏ hàng sau khi xóa sản phẩm
    return redirect('cart_detail')

#cbi cxoas
def checkout(request):
    cart = request.user.cart
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():  # Use a transaction to ensure data integrity
                order = form.save(commit=False)
                order.user = request.user
                # Assuming the first product's store is representative of the entire cart
                order.store = cart.items.first().product.store
                order.save()

                # Move cart items to order details and update stock
                insufficient_stock = []
                for item in cart.items.all():
                    if item.product.quantity >= item.quantity:  # Check if enough stock
                        item.product.quantity -= item.quantity  # Deduct stock
                        item.product.save()

                        OrderDetail.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            subtotal=item.get_total()
                        )
                    else:
                        insufficient_stock.append(item.product.name)

                if insufficient_stock:  # If any products have insufficient stock
                    # Handle insufficient stock scenario, e.g., show a message to the user
                    return render(request, 'checkout.html', {
                        'form': form,
                        'error_message': f'Insufficient stock for: {", ".join(insufficient_stock)}'
                    })

                # Clear the cart after successful transaction
                cart.items.all().delete()

                # Redirect to an order confirmation page
                return redirect('order_detail', order.id)
    else:
        form = CheckoutForm()

    return render(request, 'base/checkout_form.html', {'form': form})



@login_required
def store_order_history(request, store_id):
    stores = Store.objects.filter(owner=request.user)

    store = get_object_or_404(Store, id=store_id)
    
    
    orders = Order.objects.filter(store=store).order_by('-order_date')
    
    
    return render(request, 'base/store_order_history.html', {'store': store, 'orders': orders ,'stores':stores})



def history(request):
    # Lấy tất cả các đơn hàng của người dùng hiện tại
    order = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'base/history.html', {'order': order})

@login_required
def order_history(request):
    stores = Store.objects.filter(owner=request.user)

    orders = Order.objects.filter(user=request.user).order_by('-order_date')  # Get all orders for the user, ordered by date
    return render(request, 'base/order_history.html', {'orders': orders ,'stores':stores})


def order_detail(request, order_id):
    stores = Store.objects.filter(owner=request.user)

    order = get_object_or_404(Order, id=order_id, user=request.user)  # Ensure the order belongs to the logged-in user
    order_items = order.orderdetail_set.all()  # Retrieve all items associated with this order
    return render(request, 'base/order_detail.html', {'order': order, 'order_items': order_items,'stores':stores})




@login_required
def toggle_like(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.user in store.liker.all():
        store.liker.remove(request.user)
    else:
        store.liker.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#Event Funtion Start

def event(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    event = Event.objects.filter(
        Q(title__icontains =q) |
        Q(location__icontains = q),
        is_private = False
    )
    context = {'event':event}

    return render(request,'base/event.html',context)



#hiển thị event chi tiết
def eventDetail(request,pk):
    event = Event.objects.get(id=pk)
    
    context = {'event':event}

    return render(request,'base/event-detail.html',context)



#Hiển thị các event của tôi
def myevent(request):
    event = Event.objects.filter(host=request.user)
    context = {'event':event}
    return render(request,'base/event.html',context)

#Hiển thị các event tôi sẽ tham gia
def eventJoined(request):
    event = Event.objects.filter(par=request.user)
    context = {'event':event}
    return render(request,'base/event.html',context)


#Quan tâm đến event
def careAbout(request,pk):
    event = get_object_or_404(Event, id=pk)
    # Giả sử 'par' là một ManyToManyField liên kết với User
    event.par.add(request.user)

    # Redirect người dùng sau khi thêm vào danh sách quan tâm
    # Thay thế 'event-detail' với tên pattern URL của trang chi tiết sự kiện
    return redirect('event_detail', pk=pk)


#Bỏ quan tâm event
def discareAbout(request,pk):
    event = get_object_or_404(Event, id=pk)
    # Giả sử 'par' là một ManyToManyField liên kết với User
    event.par.remove(request.user)

    # Redirect người dùng sau khi thêm vào danh sách quan tâm
    # Thay thế 'event-detail' với tên pattern URL của trang chi tiết sự kiện
    Invitation.objects.filter(event=event, invitee=request.user).delete()
    return redirect('event_detail', pk=pk)
#event

#Tạo một Event
@login_required(login_url='login')
def createEvent(request):
    form = EventsForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            event.par.add(request.user)  # Add the host to the participants
            event.save()
            return redirect('event')
    else:
        form = EventsForm()
    context = {'form':form}
    return render(request,'base/event_form.html',context)


#Update một event
@login_required
def update_event(request, pk):
    event = get_object_or_404(Event, id=pk, host=request.user)  # Đảm bảo chỉ host mới có thể cập nhật
    if request.method == 'POST':
        form = EventsForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event-detail', pk=event.id)
    else:
        form = EventsForm(instance=event)
    return render(request, 'base/event_form.html', {'form': form})


#Xóa một event
def delete_event(request, pk):
    event = get_object_or_404(Event, id=pk, host=request.user)  # Đảm bảo chỉ host mới có thể xóa
    if request.method == 'POST':
        event.delete()
        return redirect('event')
    return render(request, 'base/delete.html', {'event': event})


#Hiển thị các bạn bè chưa tham gia vào event
def friends_not_in_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Get all accepted friendships for the user
    user_friendships = Friendship.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        status='accepted'
    )

    # Extract all friend user objects
    friends = set()
    for friendship in user_friendships:
        friend = friendship.receiver if friendship.sender == request.user else friendship.sender
        friends.add(friend)

    # Get all users who are already participating in the event
    participants = set(event.par.all())

    # Determine which friends are not participating in the event
    non_participating_friends = friends - participants

    search_query = request.GET.get('search', '')  # Get the search parameter from the URL
    if search_query:
        non_participating_friends = [friend for friend in non_participating_friends if search_query.lower() in friend.username.lower()]
    invited_ids = list(Invitation.objects.filter(event=event).values_list('invitee_id', flat=True))
    return render(request, 'base/invite.html', {
        'event': event,
        'non_participating_friends': non_participating_friends,
        'search_query': search_query,
        'invited_ids':invited_ids
    })


#Gửi lời mời tham gia vào event
def send_invitation(request, event_id, user_id):
    event = get_object_or_404(Event, pk=event_id)
    
    # Check if the user making the request is the host of the event
    if request.user != event.host:
        return HttpResponse("You are not authorized to send invitations for this event.", status=403)
    
    invitee = get_object_or_404(User, pk=user_id)
    
    # Check if an invitation has already been sent to this user for this event
    if Invitation.objects.filter(event=event, invitee=invitee).exists():
        return HttpResponse("An invitation has already been sent to this user.", status=400)

    # Check if the user is already a participant of the event
    if event.par.filter(pk=user_id).exists():
        return HttpResponse("This user is already a participant of the event.", status=400)
    
    # Create and save the new invitation
    invitation = Invitation(event=event, invitee=invitee)
    invitation.save()
    

    # Redirect to the event detail page or where you want to show the success message
    return redirect('events', event_id=event.id)

#Xem thông báo mời vào event
@login_required
def view_invitations(request):
    # Fetch invitations for the logged-in user
    invitations = Invitation.objects.filter(invitee=request.user, accepted=False)
    
    return render(request, 'base/Notification_event.html', {
        'invitations': invitations
    })

#đồng ý vào event
@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id, invitee=request.user)
    invitation.accepted = True
    invitation.save()
    # Add the user to the event participants
    invitation.event.par.add(request.user)
    return redirect('event_detail', pk=invitation.event.id)




#từ chối vào event
@login_required
def decline_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id, invitee=request.user)
    invitation.delete()
    return redirect('invitations')