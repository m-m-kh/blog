from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

import re
from django_jalali.db import models as jmodels

CUSTOM_USER = get_user_model()


class Post(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="عنوان"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        null=False,
        verbose_name="اسلاگ"
    )
    content = models.TextField(
        blank=False,
        null=False,
        verbose_name="محتوا"
    )
    author = models.ForeignKey(
        CUSTOM_USER,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="نویسنده"
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name="posts",
        verbose_name="برچسب‌ها"
    )
    likes = models.ManyToManyField(
        CUSTOM_USER,
        related_name="liked_posts",
        blank=True,
        verbose_name="لایک‌ها"
    )
    status = models.BooleanField(
        default=True,
        verbose_name="وضعیت انتشار"
    )
    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = jmodels.jDateTimeField(
        auto_now=True,
        verbose_name="تاریخ آخرین ویرایش"
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "پست"
        verbose_name_plural = "پست‌ها"

    def __str__(self):
        return self.title


def upload_media_to_path(instance, filename):
    return f"post_media/{instance.author.pk}/{filename}"


class Media(models.Model):
    file = models.FileField(
        upload_to=upload_media_to_path,
        verbose_name="فایل"
    )
    author = models.ForeignKey(
        CUSTOM_USER,
        on_delete=models.CASCADE,
        related_name="media",
        verbose_name="کاربر"
    )

    class Meta:
        verbose_name = "رسانه"
        verbose_name_plural = "رسانه‌ها"

    def __str__(self):
        return str(self.file)


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام برچسب"
    )

    def clean_name(self):
        self.name = self.name.lower()
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^`{|}~"""
        self.name = re.sub(f"[{re.escape(punctuation)}]", "", self.name)

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="پست"
    )
    author = models.ForeignKey(
        CUSTOM_USER,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="نویسنده"
    )
    content = models.TextField(
        verbose_name="متن دیدگاه"
    )
    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = jmodels.jDateTimeField(
        auto_now=True,
        verbose_name="تاریخ آخرین ویرایش"
    )
    status = models.BooleanField(
        default=True,
        verbose_name="وضعیت نمایش"
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "دیدگاه"
        verbose_name_plural = "دیدگاه‌ها"

    def __str__(self):
        return f"دیدگاه {self.author} برای {self.post}"
