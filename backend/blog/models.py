from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import re


CUSTOM_USER = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=False)
    content = models.TextField(blank=False ,null=False)
    author = models.ForeignKey(CUSTOM_USER, on_delete=models.CASCADE, related_name="posts")
    tags = models.ManyToManyField('Tag', blank=True, related_name="posts")
    likes = models.ManyToManyField(CUSTOM_USER, related_name="liked_posts")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at']

def upload_media_to_path(instance, filename):
    return f"post_media/{instance.author.pk}/{filename}"

class Media(models.Model):
    file = models.FileField(upload_to=upload_media_to_path)
    author = models.ForeignKey(CUSTOM_USER, on_delete=models.CASCADE, related_name="media")

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def clean_name(self):
        self.name = self.name.lower()
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^`{|}~"""
        self.name = re.sub(f"[{re.escape(punctuation)}]", "", self.name)


    def __str__(self):
        return self.name

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CUSTOM_USER, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']