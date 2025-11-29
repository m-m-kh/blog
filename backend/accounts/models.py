from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import gettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']