from django.contrib.auth import views as auth_views
from django.urls import path

from .views import home_redirect, landing_view, login_view, signup_view

app_name = 'accounts'

urlpatterns = [
    path('', landing_view, name='home'),
    path('home/', home_redirect, name='home_redirect'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
