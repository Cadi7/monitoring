from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FlowViewSet, FlowInstanceViewSet, StepViewSet, LogsViewSet

router = DefaultRouter(trailing_slash=False)
#
router.register(r'flows', FlowViewSet, basename='flow')
router.register(r'flow-instance', FlowInstanceViewSet, basename='flow_instance')
router.register(r'logs', LogsViewSet, basename='logs')
router.register(r'steps', StepViewSet, basename='steps')
urlpatterns = [
    path('', include(router.urls)),
]
