from datetime import datetime

from croniter import croniter
from django.utils.decorators import method_decorator
from drf_util.decorators import serialize_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import DestroyModelMixin, CreateModelMixin, ListModelMixin, RetrieveModelMixin, \
    UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet

from .helpers import StepExecution
from .models import Flow, FlowInstance, Step, Logs
from .serializers import FlowSerializer, FlowInstanceSerializer, \
    FlowUpdateStatusSerializer, StepSerializer, LogsSerializer, FlowCreateSerializer
from ..users.permissions import IsOwner


class FlowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    serializer_class = FlowSerializer
    permission_classes = [IsOwner]
    queryset = Flow.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return FlowCreateSerializer
        if self.action == "update_status":
            return FlowUpdateStatusSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @serialize_decorator(FlowUpdateStatusSerializer)
    @action(methods=['patch'], detail=True, url_path='activate', serializer_class=FlowUpdateStatusSerializer)
    def activate(self, request, *args, **kwargs):
        test_flow = get_object_or_404(Flow.objects.all(), pk=kwargs['pk'])
        test_flow.is_active = request.data['is_active']
        test_flow.next_schedule = croniter(test_flow.scheduling, datetime.utcnow()).get_next(datetime)

        test_flow.save(update_fields=['is_active', 'next_schedule'])
        return Response(FlowUpdateStatusSerializer(test_flow).data, status=HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='instances')
    def instances(self, request, *args, **kwargs):
        test_flow = get_object_or_404(Flow.objects.all(), pk=kwargs['pk'])
        instances = FlowInstance.objects.filter(test=test_flow)
        return Response(FlowInstanceSerializer(instances, many=True).data, status=HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='showsteps')
    def showsteps(self, request, *args, **kwargs):
        test_flow = get_object_or_404(Flow.objects.all(), pk=kwargs['pk'])
        steps = Step.objects.filter(flow=test_flow)
        return Response(StepSerializer(steps, many=True).data, status=HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='steps')
    @method_decorator(name='perform_bulk_create', decorator=swagger_auto_schema(
        request_body=StepSerializer(many=True), ))
    def create_steps(self, request, *args, **kwargs, ):
        test_flow = get_object_or_404(Flow.objects.all(), pk=kwargs['pk'])
        steps = [Step(**item, flow=test_flow) for item in request.data]
        Step.objects.bulk_create(steps)
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='execute')
    def execute_now(self, request, *args, **kwargs):
        flow = get_object_or_404(Flow.objects.all(), pk=kwargs['pk'])
        flow_instance = FlowInstance.objects.create(url=flow.url, browser=flow.browser, test_id=flow.id)
        StepExecution(flow_instance).execute()
        return Response(status=HTTP_200_OK)


class FlowInstanceViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = FlowInstanceSerializer
    queryset = FlowInstance.objects.all()

    @action(methods=['get'], detail=True, url_path='logs')
    def logs(self, request, *args, **kwargs):
        flow_instance = get_object_or_404(FlowInstance.objects.all(), pk=kwargs['pk'])
        logs = Logs.objects.filter(flow_instance=flow_instance)
        return Response(LogsSerializer(logs, many=True).data, status=HTTP_200_OK)

    @action(methods=['delete'], detail=False, url_path='deleteinstances')
    def delete_allinstances(self, request, *args, **kwargs):
        FlowInstance.objects.all().delete()
        return Response(status=HTTP_200_OK)

    @action(methods=['delete'], detail=False, url_path='deleteflows')
    def delete_allflows(self, request, *args, **kwargs):
        Flow.objects.all().delete()
        return Response(status=HTTP_200_OK)

    @action(methods=['delete'], detail=False, url_path='deletesteps')
    def delete_allsteps(self, request, *args, **kwargs):
        Step.objects.all().delete()
        return Response(status=HTTP_200_OK)

    @action(methods=['delete'], detail=False, url_path='deletelogs')
    def delete_alllogs(self, request, *args, **kwargs):
        Logs.objects.all().delete()
        return Response(status=HTTP_200_OK)


class StepViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin):
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class LogsViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = LogsSerializer
    queryset = Logs.objects.all()
