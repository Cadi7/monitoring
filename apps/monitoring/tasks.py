from datetime import datetime
from celery import shared_task
from croniter import croniter

from .helpers import StepExecution
from .models import Flow, FlowInstance


@shared_task
def check_flows():
    now = datetime.utcnow()
    flows = Flow.objects.filter(is_active=True, next_schedule__lte=now)
    for flow in flows:
        flow.next_schedule = croniter(flow.scheduling, now).get_next(datetime)
        flow.save(update_fields=['next_schedule'])
        execute_flow.delay(flow.id)


@shared_task(max_retries=0)
def execute_flow(flow_id):
    flow = Flow.objects.get(id=flow_id)
    flow_instance = FlowInstance.objects.create(test=flow, url=flow.url, browser=flow.browser)
    if flow_instance.status == FlowInstance.Status.PENDING:
        StepExecution(flow_instance).execute()
    else:
        raise Exception('Flow instance is not pending')

# The flows will be executed asynchronously only once, the execution will not be repeated.
# The next execution will be scheduled by the croniter library.
# The execution of the steps will be done by the StepExecution class.
# The StepExecution class will be responsible for executing the steps and saving the logs.
# The logs will be saved in the database and the attachment will be saved in the cloud.
