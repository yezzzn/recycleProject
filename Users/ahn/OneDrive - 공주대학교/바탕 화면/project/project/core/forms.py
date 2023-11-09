from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from item.models import Apartdatabase


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "아이디를 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "비밀번호를 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        # fields = ("username", "email", "password1", "password2")
        fields = ("username", "email", "password1", "password2", "phone")

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "아이디를 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "이메일을 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "비밀번호를 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "비밀번호를 다시 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "뒷 8자리 전화번호를 입력하세요",
                "class": "w-full py-4 px-6 rounded-xl",
            }
        )
    )


class ImageUploadForm(forms.Form):
    image = forms.ImageField()


class AptInfo(forms.ModelForm):
    class Meta:
        model = Apartdatabase
        fields = ["apartment", "dong", "ho"]
