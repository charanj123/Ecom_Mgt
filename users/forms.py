from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserRating

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_seller')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class CustomUserChangeForm(UserChangeForm):
    password = None
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 
                  'phone_number', 'profile_picture', 'address', 'city', 
                  'state', 'country', 'zip_code', 'is_seller')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class UserLocationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('latitude', 'longitude')
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'step': '0.000001'})
        }


class UserRatingForm(forms.ModelForm):
    class Meta:
        model = UserRating
        fields = ('rating', 'review')
        widgets = {
            'review': forms.Textarea(attrs={'rows': 3}),
            'rating': forms.RadioSelect()
        } 