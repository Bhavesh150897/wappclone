from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from .models import Profile, Message
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ),error_messages={
               'required': 'The username field is required.'
        })
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ),error_messages={
               'required': 'The email field is required.'
        })
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ),error_messages={
               'required': 'The password field is required.'
        })
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control"
            }
        ),error_messages={
               'required': 'The confirm password field is required.'
        })

    def uniqueemailvalidator(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError('User with this Email already exists.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].validators.append(self.uniqueemailvalidator)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1','password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
        

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ),error_messages={
               'required': 'The username field is required.'
        })
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ),error_messages={
               'required': 'The password field is required.'
        })

class ImageFileUploadForm(forms.ModelForm):
    avatar = forms.ImageField(label=_('Choose Image'),required=True, error_messages = {'required':'The image field is required.','invalid':_("Image files only")}, widget=forms.FileInput(attrs={'class': 'form-control custom-file-input','id' : 'customFile'}))
    bio = forms.CharField(required=True, error_messages = {'required':'This field is required.'},widget=forms.Textarea(attrs={'class':'form-control',"rows":3}))
    
    class Meta:
        model = Profile
        fields = ('avatar','bio',) 

class FileUploadForm(forms.ModelForm):
    image = forms.FileField(required=True, widget=forms.FileInput())
    
    class Meta:
        model = Message
        fields = ('image',)