from django.conf import settings
from django.urls import reverse
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from accounts.models import CustomUser

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, urlencode
from django.db.models import Q
from threading import Thread
from PIL import Image

USER_MODEL: CustomUser = get_user_model()

# celery will replace this later
class SendEmail(Thread):
    def __init__(self, user, template_name, subject, url, *args, **kwargs):
        super(SendEmail, self).__init__(*args, **kwargs)
        self.user = user
        self.template_name = template_name
        self.subject = subject
        self.url = url

    def run(self):

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(user=self.user)

        from_email = settings.EMAIL_HOST_USER

        html_content = render_to_string(self.template_name,
                                        {"username": self.user.username,
                                         'url': self.url.format(uid, token)
                                         })

        msg = EmailMultiAlternatives(self.subject, "", from_email, [self.user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

def send_confirmation_email(user, template_name, subject, url):
    SendEmail(user=user, template_name=template_name, subject=subject, url=url).start()


class UserCreationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, label='گذرواژه')
    password2 = serializers.CharField(write_only=True, label='تکرار گذرواژه')

    class Meta:
        model = USER_MODEL
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2' )


    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')
        email = data.get('email')
        username = data.get('username')
        if password1 != password2:
            raise serializers.ValidationError({'password':'دو گذرواژه یکسان نیست.'})

        try:
            temp_user = USER_MODEL(username=username, email=email)
            validate_password(password1, user=temp_user)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        return data



    def create(self, validated_data):
            validated_data.pop('password1')
            password = validated_data.pop('password2')
            user = USER_MODEL.objects.create_user(**validated_data)
            user.set_password(password)
            user.is_active = False
            user.save()

            send_confirmation_email(user, 'accounts/email_confirmation.html', "ورود به حساب کاربری",
                                    settings.FRONTEND_EMAIL_CONFIRMATION_URL)

            return user


class AuthenticationSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(label='نام کاربری یا ایمیل')
    password = serializers.CharField(write_only=True, label='گذرواژه')

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        user = USER_MODEL.objects.filter(Q(email=email_or_username) | Q(username=email_or_username), is_active=True)

        user = user.first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({'detail':'اطلاعات وارد شده معتبر نیست.'})

        return {'user': user}

class EmailConfirmationSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.CharField()

    def validate(self, data):
        token = data.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(data.get("user_id")))
            user = USER_MODEL.objects.get(pk=uid, is_active=False)
        except (USER_MODEL.DoesNotExist , ValueError):
            raise serializers.ValidationError({'detail': 'تایید ایمیل ناموفق'})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'detail': 'تایید ایمیل ناموفق'})

        return {'user': user}


class ResendEmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField(label='ایمیل')

    def validate(self, data):
        email = data.get('email')
        user = USER_MODEL.objects.filter(email=email, is_active=False).first()

        if user:
            send_confirmation_email(user, 'accounts/email_confirmation.html', "ورود به حساب کاربری",
                                settings.FRONTEND_EMAIL_CONFIRMATION_URL)
        return data

class SendResetPasswordEmailConfirmationSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(label='نام کاربری یا ایمیل')

    def validate(self, data):
        email_or_username = data.get('email_or_username')

        user = USER_MODEL.objects.filter(Q(email=email_or_username) | Q(username=email_or_username), is_active=True)

        user = user.first()

        if user:
            send_confirmation_email(user, 'accounts/reset_password.html', "بازنشانی گذرواژه", settings.FRONTEND_RESET_PASSWORD_URL)

        return {'user': user}

class ConfirmResetPasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(write_only=True, label='گذرواژه')
    password2 = serializers.CharField(write_only=True, label='تکرار گذرواژه')
    token = serializers.CharField()
    user_id = serializers.CharField()


    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')
        user_id = data.get('user_id')
        token = data.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(user_id))
            self.user = USER_MODEL.objects.get(pk=uid, is_active=True)
        except (USER_MODEL.DoesNotExist, ValueError):
            raise serializers.ValidationError({'detail': 'بازنشانی گدرواژه ناموفق'})

        if not default_token_generator.check_token(self.user, token):
            raise serializers.ValidationError({'detail': 'بازنشانی گدرواژه ناموفق'})

        if password1 != password2:
            raise serializers.ValidationError({'password':'دو گذرواژه یکسان نیست.'})

        try:
            temp_user = USER_MODEL(username=self.user.username, email=self.user.email)
            validate_password(password1, user=temp_user)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        return data


    def save(self, *args, **kwargs):
        password = self.validated_data.pop('password2')
        self.user.set_password(password)
        self.user.save()

        return self.user


class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ('username', 'email', 'first_name', 'last_name', 'last_login', 'profile_pic', 'bio')
        extra_kwargs = {
            'email': {'read_only': True},
            'last_login': {'read_only': True},
        }

class UserInformationForPostSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='username', view_name='account-user-info')

    class Meta:
        model = USER_MODEL
        fields = ('url', 'username', 'first_name', 'last_name', 'profile_pic')

class UserInformationForProfileSerializer(serializers.ModelSerializer):
    posts_url = serializers.SerializerMethodField()

    def get_posts_url(self, obj):
        request = self.context.get('request')
        path = reverse('posts-list')
        query = urlencode({'author': obj.username})
        url = request.build_absolute_uri(path)
        return url + '?' + query

    class Meta:
        model = USER_MODEL
        fields = ('username', 'first_name', 'last_name', 'profile_pic', 'bio', 'posts_url')

