from django.conf import settings
from xml.dom import ValidationErr
from rest_framework import serializers
from django.core.validators import EmailValidator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from core.models import User
from authentication.utils import Util
from django.template.loader import render_to_string
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.exceptions import ValidationError as DjangoValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.pop('password2')

        if password != password2:
            raise serializers.ValidationError({"password": "Password and Confirm password do not match"})

        # Validate the password using Django's built-in validators
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        email = attrs.get('email')
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except:
            raise serializers.ValidationError({"email": "Invalid email format. Please enter a valid email address."})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})

        return attrs

    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            name=self.validated_data['name'],
        )
        password = self.validated_data['password']
        user.set_password(password)
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        activation_link = f'http://localhost:8000/activate/{uid}/{token}'
        
        context = {
            'user': user,
            'activation_link': activation_link
        }
        
        subject = 'Activate Your Account'
        message = render_to_string('authentication/activation_email.html', context)
        
        send_mail(
            subject,
            '',
            'no-reply@example.com',
            [user.email],
            fail_silently=False,
            html_message=message
        )

        return user



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if user is None:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include both email and password.")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','email','name']

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs




class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User  # Use get_user_model() for flexibility
        fields = ['email']
    def validate(self, attrs):
        email = attrs.get('email')
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except:
            raise serializers.ValidationError("Invalid email format. Please enter a valid email address.")

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Your email is not associated with a registered user.")

        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        link = f'http://localhost:8000/reset-password/{uid}/{token}'
        body = f'Click the following link to reset your password: {link}'
        send_mail(
            'Reset Your Password',
            body,
            'no-reply@example.com',
            [user.email],
            fail_silently=False,
        )

        return attrs
    











# class UserChangePasswordSerializer(serializers.Serializer):
#     current_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
#     new_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
#     confirm_new_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

#     class Meta:
#         model=User
#         fields = ['current_password', 'new_password', 'confirm_new_password']

#     def validate(self, attrs):
#         user = self.context['request'].user
#         current_password = attrs.get('current_password')
#         new_password = attrs.get('new_password')
#         confirm_new_password = attrs.get('confirm_new_password')

#         # Check if current password matches user's password
#         if not user.check_password(current_password):
#             raise serializers.ValidationError({'current_password': 'Current password is incorrect.'})

#         # Check if new password and confirm password match
#         if new_password != confirm_new_password:
#             raise serializers.ValidationError({'confirm_new_password': 'New password and confirm password do not match.'})

#         # Validate the new password using Django's built-in validators
#         try:
#             validate_password(new_password, user=user)
#         except DjangoValidationError as e:
#             raise serializers.ValidationError({'new_password': list(e.messages)})

#         return attrs

#     def save(self):
#         user = self.context['request'].user
#         new_password = self.validated_data['new_password']
#         user.set_password(new_password)
#         user.save()
#         return user
