from django.forms import ModelForm

from .models import Room
from django.contrib.auth.models import User

from .models import Profile

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['proImg']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude =['host','participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username','email']