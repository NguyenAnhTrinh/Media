from django.contrib import admin

# Register your models here.
from .models import Room ,Topic,Message,User,Friendship,Chat


admin.site.register(Room)
admin.site.register(Chat)

admin.site.register(Friendship)

admin.site.register(User)

admin.site.register(Topic)
admin.site.register(Message)



