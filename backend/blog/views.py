from django.http import HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter as DefaultOrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import ScopedRateThrottle

from django.db.models import Q, Count, Prefetch, Exists, OuterRef
from django.utils.functional import cached_property

from django_filters.rest_framework import DjangoFilterBackend, BooleanFilter
from django_filters.rest_framework import FilterSet, CharFilter, OrderingFilter

from . import models
from . import serializer
from config.utils import format_response


class PostFilterSet(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    content = CharFilter(field_name='content', lookup_expr='icontains')
    author = CharFilter(field_name='author__username', lookup_expr='iexact')
    tags = CharFilter(method='filter_tags', help_text='فیلتر چند تگ با جدا کننده به صورت bad,good')

    ordering = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
            ('likes', 'likes'),
        )
    )

    def filter_tags(self, queryset, name, value):
        values = value.split(',')
        queryset = queryset.filter(tags__name__in=values).distinct()
        return queryset

    class Meta:
        model = models.Post
        fields = ('title', 'content', 'author', 'tags', 'ordering', 'status')


class AuthorOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            obj.author == request.user
        )


class PostsViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorOrReadOnlyPermission]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilterSet
    pagination_class = PageNumberPagination
    throttle_classes = [ScopedRateThrottle]

    @property
    def throttle_scope(self):
        if self.action == 'create':
            return 'posts-create'
        elif self.action == 'list':
            return 'posts-list'
        elif self.action == 'retrieve':
            return 'posts-retrieve'
        elif self.action == 'update':
            return 'posts-update'
        elif self.action == 'me':
            return 'posts-me'
        elif self.action == 'me_likes':
            return 'posts-me-likes'
        elif self.action == 'me_comments':
            return 'posts-me-comments'
        elif self.action == 'toggle_like':
            return 'posts-toggle-like'

    def get_queryset(self):
        queryset = models.Post.objects

        if self.action == 'list':
            queryset = queryset.annotate(
                likes_count=Count('likes'),
                liked_by_me=Exists(
                    models.Post.likes.through.objects.filter(
                        post_id=OuterRef('pk'),
                        customuser_id=self.request.user.id
                    )
                )
            ) \
                .select_related('author') \
                .prefetch_related(
                Prefetch('tags', to_attr='prefetched_tags')
            ).filter(status=True).only(
                'author__username',
                'author__first_name',
                'author__last_name',
                'author__profile_pic',
                'title', 'slug',
                'created_at', 'updated_at',
                'status'
            )

        if self.action == 'retrieve':
            queryset = queryset.annotate(
                likes_count=Count('likes'),
                liked_by_me=Exists(
                    models.Post.likes.through.objects.filter(
                        post_id=OuterRef('pk'),
                        customuser_id=self.request.user.id
                    )
                )
            ) \
                .select_related('author') \
                .prefetch_related(
                Prefetch('tags', to_attr='prefetched_tags')
            ).filter(Q(status=True) | Q(author=self.request.user)).only(
                'author__username',
                'author__first_name',
                'author__last_name',
                'author__profile_pic',
                'title', 'slug',
                'created_at', 'updated_at',
                'status'
            )

        if self.action in ['create', 'update']:
            queryset = queryset.filter(status=True).only(
                'title', 'slug',
                'created_at', 'updated_at', 'content', 'status'
            )

        if self.action == 'me':
            queryset = queryset.annotate(
                likes_count=Count('likes')
            ) \
                .select_related('author') \
                .prefetch_related(
                Prefetch('tags', to_attr='prefetched_tags')
            ).filter(Q(author=self.request.user)).only(
                'author__username',
                'author__first_name',
                'author__last_name',
                'author__profile_pic',
                'title', 'slug',
                'created_at', 'updated_at',
                'status'
            )

        if self.action == 'me_likes':
            queryset = queryset.annotate(
                likes_count=Count('likes')
            ) \
                .select_related('author') \
                .prefetch_related(
                Prefetch('tags', to_attr='prefetched_tags')
            ).filter(Q(likes=self.request.user)).only(
                'author__username',
                'author__first_name',
                'author__last_name',
                'author__profile_pic',
                'title', 'slug',
                'created_at', 'updated_at',
                'status'
            )



        return queryset

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializer.PostListSerializer

        if self.action in ['retrieve']:
            return serializer.PostRetrieveSerializer

        if self.action in ['create', 'update']:
            return serializer.PostCreateUpdateSerializer

        if self.action in ['me', 'me_likes']:
            return serializer.PostMeSerializer

        if self.action in ['me_comments']:
            return serializer.CommentMeSerializer

        return serializer.serializers.Serializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
                لیست پست هایی که کاربر احراز شده ایجاد کرده
        """

        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)

        paginated_queryset = self.paginate_queryset(queryset)

        data = self.get_serializer(paginated_queryset, many=True).data

        return self.get_paginated_response(data)

    @action(detail=False, methods=['get'], url_path='me/likes', permission_classes=[IsAuthenticated])
    def me_likes(self, request):
        """
            لیست پست هایی که کاربر احراز شده لایک کرده
        """

        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)

        paginated_queryset = self.paginate_queryset(queryset)

        data = self.get_serializer(paginated_queryset, many=True).data

        return self.get_paginated_response(data)

    @action(detail=False, methods=['get'], url_path='me/comments', permission_classes=[IsAuthenticated])
    def me_comments(self, request):
        """
            لیست کامنت هایی که کاربر احراز شده ثبت کرده
        """

        queryset = models.Comment.objects.select_related('post').filter(author=self.request.user)

        paginated_queryset = self.paginate_queryset(queryset)

        data = self.get_serializer(paginated_queryset, many=True).data

        return self.get_paginated_response(data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, slug=None):
        user = request.user
        post = get_object_or_404(
            models.Post,
            slug=slug
        )

        if post.author_id == user.id:
            return Response(format_response(
                success=False,
                message='روی پست خود نمی‌توانید درخواست انجام دهید'
            ))

        liked = post.likes.filter(id=user.id).exists()

        if liked:
            post.likes.remove(user)
        else:
            post.likes.add(user)

        like_count = post.likes.count()

        return Response(format_response(
            success=True,
            message={
                'liked': not liked,
                'like_count': like_count,
            }
        ))


class MediaViewSet(viewsets.ModelViewSet):
    serializer_class = serializer.MediaSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]

    @property
    def throttle_scope(self):
        if self.action == 'create':
            return 'media-create'
        elif self.action == 'list':
            return 'media-list'
        elif self.action == 'retrieve':
            return 'media-retrieve'
        elif self.action == 'update':
            return 'media-update'

    def get_queryset(self):
        queryset = models.Media.objects.filter(author=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializer.TagsSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DefaultOrderingFilter]
    ordering_fields = ['posts_count']

    def get_queryset(self):
        queryset = models.Tag.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__status=True)),
        )
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializer.CommentSerializer
    permission_classes = [AuthorOrReadOnlyPermission]
    filter_backends = [DefaultOrderingFilter]
    ordering_fields = ('created_at', 'updated_at')
    pagination_class = PageNumberPagination
    throttle_classes = [ScopedRateThrottle]

    @property
    def throttle_scope(self):
        if self.action == 'create':
            return 'comment-create'
        elif self.action == 'update':
            return 'comment-update'

    @cached_property
    def post_obj(self):
        slug = self.kwargs.get("post_slug")
        if not slug:
            return None
        return get_object_or_404(models.Post, slug=slug)


    def get_queryset(self):
        queryset = models.Comment.objects.select_related('author').filter(status=True, post=self.post_obj)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.post_obj)


@api_view(['GET'])
def media(request, path):
    print(path)
    response = HttpResponse()
    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = f'/private_media/{path}'
    return response
