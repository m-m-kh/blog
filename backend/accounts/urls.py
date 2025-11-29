from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('auth', views.AuthViewSet)

urlpatterns = router.urls