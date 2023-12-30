# from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name="home"),
    path('room/<str:pk>/',views.room,name="room"),
    path('create-room/',views.createRoom, name ="create-room"),
    path('update-room/<slug:pk>/',views.updateRoom, name ="update-room"),
    path('delete-room/<slug:pk>/',views.deleteRoom, name ="delete-room"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('sign/',views.sign,name="sign"),
    path('profile/<str:pk>/',views.userProfile,name="profile"),
    path('delete-message/<str:pk>/',views.deleteMessage, name ="delete-message"),
    path('update-user/',views.updateUser, name ="update-user"),
    path('topics/',views.topicsPage, name ="topics"),
    path('friend/',views.friendPages, name ="friend"),
    path('myfriend/',views.myFriends, name ="myfriend"),


    path('activity/',views.activityPages, name ="activity"),


    path('update_avatar/', views.update_avatar, name='update_avatar'),

    path('addFriend/<str:pk>/',views.sentRequest,name="addFriend"),
    path('accept/<str:pk>/',views.acceptRequest,name = 'accept'),
    path('reject/<str:pk>/',views.reject, name = 'reject'),

    



]