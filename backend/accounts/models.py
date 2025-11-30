from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import gettext_lazy as _
from PIL import Image
from shortuuid import uuid


def profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.pk}.{ext}"
    return f"profile_images/{filename}"

class CustomUser(AbstractUser):
    id = models.CharField(primary_key=True, default=uuid, editable=False, unique=True)
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    profile_pic = models.ImageField("تصویر پروفایل", upload_to=profile_upload_path, null=True, blank=True, default=None)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.profile_pic:
            img_path = self.profile_pic.path
            img = Image.open(img_path)


            max_size = (400, 400)
            img.thumbnail(max_size)


            if img.format != "JPEG":
                img = img.convert("RGB")

            img.save(img_path, format="JPEG", quality=70, optimize=True)