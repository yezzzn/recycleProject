from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import LoginForm

app_name = "core"

urlpatterns = [
    path("", views.first, name="first"),
    path("example/", views.get),
    path("index/", views.index, name="index"),
    path("cindex/", views.cindex, name="cindex"),
    path("signup/", views.signup, name="signup"),
    path("milli/", views.milli, name="milli"),
    path("update_point/", views.update_point),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="core/login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("save_apt_info/", views.save_apt_info, name="save_apt_info"),
    path("email/", views.email_comp, name="email"),
]
