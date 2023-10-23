from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.monitoring.helpers import StepExecution
from apps.monitoring.models import FlowInstance


@receiver(post_save, sender=FlowInstance)
def signal_execute(sender, instance, **kwargs):
    if instance.status == "in_progress":
        StepExecution(instance).execute()
