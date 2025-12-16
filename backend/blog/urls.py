from django.urls import path
from rest_framework_nested.routers import NestedDefaultRouter, DefaultRouter
from . import views

router = DefaultRouter()

router.register('posts', views.PostsViewSet, basename='posts')
router.register('post_media', views.MediaViewSet, basename='post_media')
router.register('tags', views.TagsViewSet, basename='tags')

nested_router = NestedDefaultRouter(router, 'posts', lookup='post')
nested_router.register('comment', views.CommentViewSet, basename='comment')

urlpatterns = [
    *router.urls,
    *nested_router.urls,
]