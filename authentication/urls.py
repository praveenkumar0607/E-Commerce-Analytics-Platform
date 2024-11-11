from django.urls import path
from . import views
from authentication.views import UserRegistrationView,UserLoginView,UserActivateView,UserProfileView,SendPasswordResetEmailView,UserPasswordResetView,ActivateUserView
# from .views import ProtectedHtmlView


urlpatterns = [
    path('', views.Account, name='account'),
    path('home/', views.Home, name='home'),
    path('signout/',views.Signout,name='signout'),
    path('signup/',UserRegistrationView.as_view(),name='signup'),
    path('signin/',UserLoginView.as_view(),name='signin'),
    path('authenticate/<uidb64>/<token>/', UserActivateView.as_view(), name='user-activate'),
    path('activate/<str:uidb64>/<str:token>/', ActivateUserView.as_view(), name='activate'),
    # path('profile/',UserProfileView.as_view(),name='profile'),
    # path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-email/', SendPasswordResetEmailView.as_view(), name='send-reset-email'),
    path('reset-password/<uidb64>/<token>/', UserPasswordResetView.as_view(), name='reset_password'),
    # path('protectedhtml/', ProtectedHtmlView.as_view(), name='protectedhtml'),
]
