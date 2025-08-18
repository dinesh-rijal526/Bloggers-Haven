# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "Username"
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "Name"
        })
    )
    
    avatar = forms.ImageField(
        required=False,
        label="Profile Picture",
        widget=forms.FileInput(attrs={
            "class": "input",
            "accept": "image/*",
        }),
    )

    class Meta:
        model = Profile
        fields = ["username", "first_name",  "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Tell us about yourself...",
                "class": "input",
            }),
        }
        labels = {
            "bio": "About Me",
            "avatar": "Profile Picture",
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['first_name'].initial = self.user_instance.first_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if (User.objects.exclude(pk=self.user_instance.pk)
                       .filter(username=username).exists()):
            raise forms.ValidationError("This username is already taken")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        self.user_instance.username = self.cleaned_data['username']
        self.user_instance.first_name = self.cleaned_data['first_name']
        self.user_instance.save()
        
        if commit:
            profile.save()
        return profile