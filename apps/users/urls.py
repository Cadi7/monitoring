from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.users.views import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    *router.urls,
]
