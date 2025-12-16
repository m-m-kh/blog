from rest_framework import serializers

from . import models
from accounts.serializers import UserInformationForPostSerializer
from django.urls import reverse
from django.utils.http import urlencode

import bleach

class TagsSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    posts_url = serializers.SerializerMethodField()

    def get_posts_count(self, obj):
        return obj.posts_count

    def get_posts_url(self, obj):
        request = self.context.get('request')
        path = reverse('posts-list')
        query = urlencode({'tags': obj.name})
        url = request.build_absolute_uri(path)
        return url + '?' + query



    class Meta:
        model = models.Tag
        fields = ['name', 'posts_count', 'posts_url']

class StringListSerializer(serializers.ListSerializer):
    child = serializers.CharField()

class PostListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='slug', view_name='posts-detail')
    author = UserInformationForPostSerializer(read_only=True)
    tags_list = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    you_liked = serializers.SerializerMethodField()

    def get_tags_list(self, obj):
        return [i.name for i in obj.prefetched_tags]

    def get_likes(self, obj):
        return obj.likes_count

    def get_you_liked(self, obj):
        return getattr(obj, 'you_liked', False)

    class Meta:
        model = models.Post
        exclude = ('id', 'content', 'tags')

class PostRetrieveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='slug', view_name='posts-detail')
    comment_url = serializers.HyperlinkedIdentityField(lookup_field='slug', lookup_url_kwarg='post_slug', view_name='comment-list')
    author = UserInformationForPostSerializer(read_only=True)
    tags_list = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    you_liked = serializers.SerializerMethodField()

    def get_tags_list(self, obj):
        return [i.name for i in obj.prefetched_tags]

    def get_likes(self, obj):
        return obj.likes_count

    def get_you_liked(self, obj):
        return getattr(obj, 'you_liked', False)

    class Meta:
        model = models.Post
        exclude = ('id', 'tags')

class PostMeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='slug', view_name='posts-detail')
    tags_list = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()


    def get_tags_list(self, obj):
        return [i.name for i in obj.prefetched_tags]

    def get_likes(self, obj):
        return obj.likes_count

    class Meta:
        model = models.Post
        exclude = ('id', 'content', 'tags', 'author')


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='slug', view_name='posts-detail')
    tags_list = serializers.ListField(child=serializers.CharField(), required=False)

    ALLOWED_TAGS = [
        'p', 'br',
        'b', 'strong', 'i', 'em', 'u',
        'h1', 'h2', 'h3', 'h4',
        'ul', 'ol', 'li',
        'blockquote',
        'code', 'pre',
        'a',
        'img',
    ]

    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'rel'],
        'img': ['src', 'alt', 'title'],
        '*': ['class'],  # اختیاری (برای editor)
    }

    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

    class Meta:
        model = models.Post
        exclude = ('id', 'likes', 'author', 'tags')
        extra_kwargs = {'slug': {'read_only': True}}

    def validate_content(self, content):
        cleaned = bleach.clean(
            content,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            protocols=self.ALLOWED_PROTOCOLS,
            strip=True
        )

        return cleaned

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        tags = set(tags)


        if not tags:
            instance.tags.clear()
            return instance

        exists_tags = models.Tag.objects.filter(name__in=tags)
        exists_names = {t.name for t in exists_tags}

        new_names = tags - exists_names
        new_tag_objs = []
        if new_names:
            for name in new_names:
                obj = models.Tag(name=name)
                obj.clean_name()
                new_tag_objs.append(obj)
            new_tag_objs = models.Tag.objects.bulk_create(new_tag_objs)


        instance.tags.set([*exists_tags, *new_tag_objs])


        return instance

    def create(self, validated_data):
        tags = validated_data.pop('tags_list', [])
        tags = set(tags)

        exists_tags = models.Tag.objects.filter(name__in=tags)
        exists_names = {t.name for t in exists_tags}

        new_names = tags - exists_names
        new_tag_objs = []
        if new_names:
            for name in new_names:
                obj = models.Tag(name=name)
                obj.clean_name()
                new_tag_objs.append(obj)
            new_tag_objs = models.Tag.objects.bulk_create(new_tag_objs)

        instance = models.Post.objects.create(**validated_data)
        instance.tags.set([*exists_tags, *new_tag_objs])

        return instance



class MediaSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='post_media-detail')
    class Meta:
        model = models.Media
        exclude = ('author',)
        extra_kwargs = {
                'author': {'read_only': True},
            }


class CommentSerializer(serializers.ModelSerializer):
    author = UserInformationForPostSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    post_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        exclude = ('id', 'post', 'status')

    def get_url(self, obj):
        request = self.context.get('request')
        view = self.context.get('view')
        post_slug = view.kwargs.get('post_slug') or obj.post.slug
        path = reverse('comment-detail', args=[post_slug ,obj.pk])
        url = request.build_absolute_uri(path)
        return url

    def get_post_url(self, obj):
        request = self.context.get('request')
        view = self.context.get('view')
        post_slug = view.kwargs.get('post_slug') or obj.post.slug
        path = reverse('posts-detail', args=[post_slug])
        url = request.build_absolute_uri(path)
        return url

class CommentMeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    post_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        exclude = ('id', 'post', 'status', 'author')

    def get_url(self, obj):
        request = self.context.get('request')
        view = self.context.get('view')
        post_slug = view.kwargs.get('post_slug') or obj.post.slug
        path = reverse('comment-detail', args=[post_slug ,obj.pk])
        url = request.build_absolute_uri(path)
        return url

    def get_post_url(self, obj):
        request = self.context.get('request')
        view = self.context.get('view')
        post_slug = view.kwargs.get('post_slug') or obj.post.slug
        path = reverse('posts-detail', args=[post_slug])
        url = request.build_absolute_uri(path)
        return url