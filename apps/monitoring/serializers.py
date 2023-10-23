from abc import ABC

from rest_framework import serializers

from .models import Flow, FlowInstance, Step, Logs


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = "__all__"
        read_only_fields = ("flow",)


class FlowSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Flow
        fields = "__all__"
        extra_kwargs = {"steps": {"read_only": True}}


class FlowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flow
        fields = "__all__"
        read_only_fields = ("user", "next_schedule")


class FlowUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flow
        fields = ("id", "is_active",)


class FlowInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowInstance
        fields = "__all__"


class LogsSerializer(serializers.ModelSerializer):
    step = StepSerializer(read_only=True)
    class Meta:
        model = Logs
        fields = "__all__"
        read_only_fields = ("step",)
