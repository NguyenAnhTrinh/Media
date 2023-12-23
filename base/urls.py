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
    path('update_avatar/', views.update_avatar, name='update_avatar'),
    # path('update_avatar/', views.update_avatar, name='update_avatar'),

]