from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from user.api.views import (
    registration_view,
    logout_view,
    login_view
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', registration_view, name='register'),
]
