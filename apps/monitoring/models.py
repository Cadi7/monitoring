from django.conf import settings
from django.db import models
from django.utils import timezone


# Create your models here.
class Flow(models.Model):
    class BrowserInstance(models.TextChoices):
        CHROME = 'chrome'
        FIREFOX = 'firefox'

    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True)

    browser = models.CharField(max_length=30, choices=BrowserInstance.choices,
                               default=BrowserInstance.CHROME)
    scheduling = models.CharField(max_length=254)
    next_schedule = models.DateTimeField(null=True, default=None)
    is_active = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class FlowInstance(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        IN_PROGRESS = "in_progress"
        SUCCESS = "success"
        FAIL = "fail"

    url = models.URLField()
    browser = models.CharField(max_length=30, choices=Flow.BrowserInstance.choices,
                               default=Flow.BrowserInstance.CHROME)
    started_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    test = models.ForeignKey(Flow, on_delete=models.CASCADE)


class Step(models.Model):
    class Action(models.TextChoices):
        CLICK = "click"
        TAPPING = "tapping"
        SUBMIT = "submit"
        CLEAR = "clear"
        ENTER = "enter"
    step_number = models.IntegerField()
    action = models.CharField(max_length=254, choices=Action.choices)
    selector_xpath = models.CharField(max_length=254)
    content = models.CharField(max_length=254, blank=True)
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name="steps")

    def __str__(self):
        return self.action


class Logs(models.Model):
    class Status(models.TextChoices):
        INITIAL = "initial"
        SUCCESS = "success"
        FAIL = "fail"
        FINAL = "final"

    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    attachment = models.URLField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIAL)
    additional_data = models.JSONField(default=dict)
    flow_instance = models.ForeignKey(FlowInstance, on_delete=models.CASCADE)
