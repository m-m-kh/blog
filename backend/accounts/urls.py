from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('account', views.AccountViewSet, basename='account')


urlpatterns = [
    *router.urls
]