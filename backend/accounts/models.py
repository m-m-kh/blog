from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import gettext_lazy as _
from shortuuid import uuid
from pathlib import Path
from django.conf import settings

from django_jalali.db import models as jmodels

def profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.pk}.{ext}"
    file_path = Path(settings.MEDIA_ROOT.joinpath(f"profile_images/{filename}"))

    if file_path.parent.exists():
        file_path.unlink()

    return file_path

class CustomUser(AbstractUser):
    id = models.CharField(primary_key=True, default=uuid, editable=False, unique=True)
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    profile_pic = models.ImageField("تصویر پروفایل", upload_to=profile_upload_path, null=True, blank=True, default=None)
    bio = models.TextField('بیوگرافی', null=True, blank=True, max_length=500)
    last_login = jmodels.jDateTimeField(_("last login"), blank=True, null=True)
    date_joined = jmodels.jDateTimeField(_("date joined"), default=timezone.now)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
