import socket
from django.shortcuts import render, redirect
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer
)
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from core.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from smtplib import SMTPAuthenticationError


# class ProtectedHtmlView(LoginRequiredMixin, TemplateView):
#     template_name = 'protect.html'  # This should be the base template for your protected HTML files

def Account(request):
    return render(request, 'authentication/register.html')


@login_required
def Home(request):
    return render(request, 'home.html')

@login_required  
def Signout(request):
    logout(request)
    get_token(request)
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'authentication/register.html') # Redirect to the sign-in page after logout


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authentication/register.html'

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'msg': 'Registration email has been sent. Please check your email to activate your account.'},
                status=status.HTTP_201_CREATED,
                template_name='authentication/success.html'
            )
        else:
            errors = serializer.errors
            if 'email' in errors:
                if 'A user with that email already exists.' in errors['email'][0]:
                    return self.handle_email_exists(request)
                else:
                    return self.handle_invalid_email(request)
            elif 'password' in errors:
                if 'Password and Confirm password do not match' in errors['password'][0]:
                    return self.handle_password_mismatch(request)
                else:
                    return self.handle_password_error(request, errors['password'])
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST,
                template_name=self.template_name
            )

    def handle_invalid_email(self, request):
        return Response(
            {'error_msg': 'Invalid email format. Please enter a valid email address.'},
            status=status.HTTP_400_BAD_REQUEST,
            template_name='authentication/registration_error.html'
        )

    def handle_password_mismatch(self, request):
        return Response(
            {'error_msg': 'Password and Confirm password do not match.'},
            status=status.HTTP_400_BAD_REQUEST,
            template_name='authentication/password_mismatch_error.html'
        )

    def handle_password_error(self, request, errors):
        return Response(
            {'error_msg': errors},
            status=status.HTTP_400_BAD_REQUEST,
            template_name='authentication/password_error.html'
        )

    def handle_email_exists(self, request):
        return Response(
            {'error_msg': 'A user with that email already exists. Please login.'},
            status=status.HTTP_400_BAD_REQUEST,
            template_name='authentication/email_exists.html'
        )
class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token, format=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('signin')  # Redirect to signin page after successful activation
        else:
            return Response({'msg': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)




class UserLoginView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authentication/register.html'  # Path to your HTML template

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to the home page
        else:
            email = request.data.get('email')
            if email:
                user = User.objects.filter(email=email).first()
                if user:
                    try:
                        self.send_login_link(user)
                    except SMTPAuthenticationError:
                        return Response(
                            {'msg': 'Invalid email credentials. Please check your email settings.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            template_name='authentication/error.html'
                        )
                    except socket.gaierror:
                        return Response(
                            {'msg': 'There was an issue sending the login link. Please try again later.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            template_name='authentication/error.html'
                        )
            return Response({'errors': serializer.errors, 'msg': 'Check your email for the login link.'}, status=status.HTTP_400_BAD_REQUEST, template_name='authentication/invalid_login.html')

    def send_login_link(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        link = f'http://localhost:8000/authenticate/{uid}/{token}/'
        subject = 'Login to Nighwan Technology using the below link'
        context = {
            'user': user,
            'link': link
        }

        message = render_to_string('authentication/login_email.html', context)

        try:
            send_mail(
                subject,
                '',
                'no-reply@example.com',
                [user.email],
                fail_silently=False,
                html_message=message
            )
        except SMTPAuthenticationError as e:
            raise e
        except Exception as e:
            raise e
class UserActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token, format=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to the home page
        else:
            return Response({'msg': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    def get(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}
        return render(request, 'authentication/reset_password.html', context)

    def post(self, request, uidb64, token):
        serializer = UserPasswordResetSerializer(data=request.POST)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if PasswordResetTokenGenerator().check_token(user, token):
                    user.set_password(serializer.validated_data['password'])
                    user.save()
                    return render(request, 'authentication/reset_password_success.html')
                else:
                    return render(request, 'authentication/reset_password_invalid_link.html')
            except User.DoesNotExist:
                return render(request, 'authentication/reset_password_invalid_link.html')
        return render(request, 'authentication/reset_password.html', {'errors': serializer.errors, 'uidb64': uidb64, 'token': token})






class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes=[IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SendPasswordResetEmailView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authentication/forgetpassword.html'  # Path to your HTML template

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            # Logic to send reset email (not shown here)
            return Response({'msg': 'Password Reset link sent. Please check your email.'}, status=status.HTTP_200_OK)
        else:
            # If serializer is not valid, return errors and render template
            return Response({'serializer': serializer}, template_name=self.template_name)
    




# class UserChangePasswordView(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'authentication/change_password.html'
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         serializer = UserChangePasswordSerializer()
#         return Response({'serializer': serializer}, template_name=self.template_name)

#     def post(self, request, *args, **kwargs):
#         serializer = UserChangePasswordSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK, template_name='authentication/change_password_success.html')
#         else:
#             return Response({'serializer': serializer, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST, template_name=self.template_name)
