from django.urls import path
from . import views
from blog.urls import router


router.register('account', views.AccountViewSet, basename='account')


urlpatterns = [
    *router.urls
]