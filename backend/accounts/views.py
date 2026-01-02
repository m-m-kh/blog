from django.utils import timezone
from django.views.decorators.csrf import get_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.throttling import ScopedRateThrottle, UserRateThrottle
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import Serializer

from django.contrib.auth import login, logout
from django.contrib.auth.models import Group

from . import serializers
from .models import CustomUser
from config.utils import format_response

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, extend_schema_view


class IsAnonymousUser(BasePermission):
    def has_permission(self, request, view):
        return not bool(request.user and request.user.is_authenticated)

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class AccountViewSet(GenericViewSet):
    throttle_classes = [ScopedRateThrottle]

    @property
    def throttle_scope(self):
        if self.action == 'me' and self.request.method in SAFE_METHODS:
            return 'me_get'
        if self.action == 'me':
            return 'me_update'
        if self.action == 'login':
            return 'login'
        if self.action == 'signup':
            return 'signup'
        if self.action == 'user_info':
            return 'user_info'
        if self.action == 'email_confirmation':
            return 'email_confirmation'
        if self.action == 'confirm_reset_password':
            return 'confirm_reset_password'

        if self.action in [
            'resend_email_confirmation',
            'send_reset_password_email_confirmation'
        ]:
            return 'send_email'

        return None

    def get_serializer_class(self):
        action_serializers = {
            'signup': serializers.UserCreationSerializer,
            'login': serializers.AuthenticationSerializer,
            'email_confirmation': serializers.EmailConfirmationSerializer,
            'resend_email_confirmation': serializers.ResendEmailConfirmationSerializer,
            'send_reset_password_email_confirmation': serializers.SendResetPasswordEmailConfirmationSerializer,
            'confirm_reset_password': serializers.ConfirmResetPasswordSerializer,
            'me': serializers.UserInformationSerializer,
            'user_info': serializers.UserInformationForProfileSerializer,
        }
        return action_serializers.get(self.action, Serializer)

    def list(self, request, *args, **kwargs):
        return Response(self.get_extra_action_url_map())

    @extend_schema(
        description="Endpoint to set CSRF cookie for frontend",
        responses={200: {"detail": "CSRF cookie set"}}
    )
    @action(detail=False, methods=['get'])
    def get_csrf(self, request):
        get_token(request)
        return Response({"detail": "CSRF cookie set"}, status=200)

    @extend_schema(
        summary="User signup",
        description="Register a new user and send a confirmation email.",
        request=serializers.UserCreationSerializer,
        responses={
            201: {
                "success": True,
                "message": "یک ایمیل برای تایید هویت ارسال شد."
            },
            400: {"description": "Validation error"}
        },
        examples=[
            OpenApiExample(
                name="Signup request example",
                value={
                    "username": "john_doe",
                    "email": "john@example.com",
                    "password": "StrongPass123"
                },
                request_only=True
            ),
            OpenApiExample(
                name="Signup response example",
                value={
                    "success": True,
                    "message": "یک ایمیل برای تایید هویت ارسال شد."
                },
                response_only=True
            )
        ]
    )
    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def signup(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            format_response(success=True, message='یک ایمیل برای تایید هویت ارسال شد.'),
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="User login",
        description="Authenticate user with email and password.",
        request=serializers.AuthenticationSerializer,
        responses={
            200: {
                "success": True,
                "message": "ورود موفق."
            },
            400: {"description": "Invalid credentials"}
        },
        examples=[
            OpenApiExample(
                name="Login request example",
                value={
                    "email": "john@example.com",
                    "password": "StrongPass123"
                },
                request_only=True
            ),
            OpenApiExample(
                name="Login response example",
                value={
                    "success": True,
                    "message": "ورود موفق."
                },
                response_only=True
            )
        ]
    )
    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(
            format_response(success=True, message='ورود موفق.'),
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="User logout",
        description="Logout the currently authenticated user.",
        responses={
            200: {
                "success": True,
                "message": "خروج موفق."
            }
        }
    )
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated], throttle_classes=[])
    def logout(self, request):
        logout(request)
        return Response(
            format_response(success=True, message='خروج موفق.'),
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Confirm email",
        description="Activate user account by confirming email.",
        request=serializers.EmailConfirmationSerializer,
        responses={
            200: {
                "success": True,
                "message": "ایمیل تایید شد."
            },
            400: {"description": "Invalid token or request"}
        },
    )
    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def email_confirmation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.is_active = True
        user.last_login = timezone.now()
        user.save()
        return Response(
            format_response(success=True, message='ایمیل تایید شد.'),
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Resend email confirmation",
        description="Resend the account confirmation email.",
        request=serializers.ResendEmailConfirmationSerializer,
        responses={
            200: {
                "success": True,
                "message": "ایمیل احراز هویت مجدد ارسال شد."
            },
            400: {"description": "Validation error"}
        }
    )
    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def resend_email_confirmation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            format_response(success=True, message='ایمیل احراز هویت مجدد ارسال شد.'),
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Send reset password email",
        description="Send an email to reset the user's password.",
        request=serializers.SendResetPasswordEmailConfirmationSerializer,
        responses={
            200: {
                "success": True,
                "message": "ایمیل بازنشانی گذرواژه ارسال شد."
            },
            400: {"description": "Validation error"}
        }
    )
    @action(methods=['post'], detail=False)
    def send_reset_password_email_confirmation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            format_response(success=True, message='ایمیل بازنشانی گذرواژه ارسال شد.'),
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Confirm password reset",
        description="Confirms the password reset process using the provided token or code.",
        request=serializers.ConfirmResetPasswordSerializer,
        responses={
            200: {
                "success": True,
                "message": "بازنشانی گذرواژه باموفقیت انجام شد."
            },
            400: {"description": "Invalid token or validation error"}
        },
        examples=[
            OpenApiExample(
                name="Confirm reset password request example",
                value={
                    "token": "abcdef123456",
                    "new_password": "NewPassword123"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Confirm reset password response example",
                value={
                    "success": True,
                    "message": "بازنشانی گذرواژه باموفقیت انجام شد."
                },
                response_only=True,
            )
        ]
    )
    @action(methods=['post'], detail=False, )
    def confirm_reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            format_response(success=True, message='بازنشانی گذرواژه باموفقیت انجام شد.'),
            status=status.HTTP_200_OK
        )

    @extend_schema(
        methods=['get'],
        summary="Get current user information",
        description="Returns the currently authenticated user's information.",
        responses=serializers.UserInformationSerializer,

    )
    @extend_schema(
        methods=['patch'],
        summary="Update current user information",
        description="Updates fields of the currently authenticated user.",
        request=serializers.UserInformationSerializer,
        responses=serializers.UserInformationSerializer,

    )
    @action(methods=['get', 'patch'],
            detail=False,
            permission_classes=[IsAuthenticated],
            )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(instance=request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.get_serializer(instance=request.user)

        return Response(format_response(
            success=True,
            message=serializer.data,
        ))

    @extend_schema(
        summary="Get user information by username",
        description="This endpoint returns the details of a user given their username.",
        parameters=[
            OpenApiParameter(
                name="username",
                description="The username of the user to retrieve",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: serializers.UserInformationForProfileSerializer,
            404: {"description": "User not found"}
        },

    )
    @action(methods=['get'],
            detail=False, url_path='(?P<username>[^/.]+)')
    def user_info(self, request, username=None):
        user_obj = get_object_or_404(CustomUser, username=username)
        serializer = self.get_serializer(instance=user_obj)

        return Response(
            serializer.data
        )

    @action(methods=['post'],
            detail=False, url_path='(?P<username>[^/.]+)/set_author',
            permission_classes=[IsSuperUser])
    def toggle_author_permission(self, request, username=None):
        user_obj = get_object_or_404(CustomUser, username=username)

        author_group = Group.objects.get_or_create(name='author')[0]

        if author_status := user_obj.groups.filter(name='author').exists():
            user_obj.groups.remove(author_group)
        else:
            user_obj.groups.add(author_group)


        return Response(
            not author_status
        )