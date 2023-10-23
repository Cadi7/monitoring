from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.monitoring.helpers import StepExecution
from apps.monitoring.models import Flow, FlowInstance, Step
from apps.users.models import User


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class TestExecution(APITestCase):
    def setUp(self):
        email = "tster@gmail.com"
        password = "1234"
        self.user = User.objects.create_user(email, email, password)
        self.user.is_confirmed = True
        token = get_tokens_for_user(self.user).get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.flow = Flow.objects.create(name="tstEBS", url="https://www.google.com/", browser="chrome",
                                        scheduling="*/2 * * * *", user=self.user)

        Step.objects.create(flow=self.flow, action='click',
                            selector_xpath="//div[@class='FPdoLc lJ9FBc']//input[@name='btnI']", )
        Step.objects.create(flow=self.flow, action='click', selector_xpath="//a[@id='latest-title']", )
        Step.objects.create(flow=self.flow, action='click', selector_xpath="//input[@id='searchinput']", )
        Step.objects.create(flow=self.flow, action='tapping', selector_xpath="//input[@id='searchinput']",
                            content='test')

        self.flowinstance = FlowInstance.objects.create(url="https://www.google.com/", browser="chrome", test=self.flow)

    def test_execution(self):
        StepExecution(self.flowinstance).execute()
        self.assertEqual(self.flowinstance.status, FlowInstance.Status.SUCCESS)


class TestFlow(APITestCase):
    def setUp(self):
        email = "mailuc@gmail.com"
        password = "1234"
        self.user = User.objects.create_user(email, email, password)
        self.user.is_confirmed = True
        token = get_tokens_for_user(self.user).get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.flow = Flow.objects.create(name="tstEBS", url="https://www.google.com/", browser="chrome", user=self.user)

    def test_createsteps(self):
        data = {
            "steps": [
                {
                    "action": "click",
                    "selector_xpath": "//div[@class='FPdoLc lJ9FBc']//input[@name='btnI']",
                },
                {
                    "action": "click",
                    "selector_xpath": "//a[@id='latest-title']",
                },
                {
                    "action": "click",
                    "selector_xpath": "//input[@id='searchinput']",
                },
                {
                    "action": "tapping",
                    "selector_xpath": "//input[@id='searchinput']",
                    "content": "test"
                }
            ]
        }
        response = self.client.post(f"/monitoring/flows/{self.flow.id}/steps/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Step.objects.count(), 4)

    def test_bad_steps(self):
        data = {
            "steps": [
                {
                    "action": "cluck",
                    "selector_xpath": "//div[@class='FPdoLc lJ9FBc']//input[@name='btnI']",
                },
                {
                    "action": "click",
                    "selectdor_xpath": "//a[@id='latest-title']",
                }
            ]
        }
        response = self.client.post(f"/monitoring/flows/{self.flow.id}/steps/", data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_get_flows(self):
        response = self.client.get("/monitoring/flows/")
        self.assertEqual(response.status_code, 200)

    def test_updateflow(self):
        data = {
            "name": "aoloo",
            "url": "https://www.google.com/",
            "browser": "chrome",
            "scheduling": "*/2 * * * *",
            "is_active": True
        }

        response = self.client.put(f"/monitoring/flows/{self.flow.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Flow.objects.first().name, "aoloo")


class TestFlowInstance(APITestCase):
    def setUp(self):
        email = "tester@gmail.com"
        password = "123"
        self.user = User.objects.create_user(email, email, password)
        self.user.is_confirmed = True
        token = get_tokens_for_user(self.user).get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.flow = Flow.objects.create(name="tstEBS", url="https://www.google.com/", browser="chrome",
                                        scheduling="*/2 * * * *", user=self.user)
        Step.objects.create(flow=self.flow, action='click',
                            selector_xpath="//div[@class='FPdoLc lJ9FBc']//input[@name='btnI']", )
        Step.objects.create(flow=self.flow, action='click', selector_xpath="//a[@id='latest-title']", )
        Step.objects.create(flow=self.flow, action='click', selector_xpath="//input[@id='searchinput']", )
        Step.objects.create(flow=self.flow, action='tapping', selector_xpath="//input[@id='searchinput']",
                            content='test')

        self.flowinstance = FlowInstance.objects.create(url="https://www.google.com/", browser="chrome", test=self.flow)

    def test_flowinstance_list(self):
        response = self.client.get(f'/monitoring/flow-instance/')
        self.assertEqual(response.status_code, 200)

    def test_flowinstance_logs(self):
        StepExecution(self.flowinstance).execute()
        response = self.client.get(f'/monitoring/flow-instance/{self.flowinstance.id}/logs/')
        self.assertEqual(response.status_code, 200)

    def test_flowinstance_fail(self):
        Step.objects.create(flow=self.flow, action='click',
                            selector_xpath="navem", )

        StepExecution(self.flowinstance).execute()
        response = self.client.get(f'/monitoring/flow-instance/{self.flowinstance.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], FlowInstance.Status.FAIL)

    def test_activate_flow(self):
        data = {
            "is_active": True
        }
        response = self.client.patch(f'/monitoring/flows/{self.flow.id}/activate/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_active'], True)

    def test_flowinstance_success(self):
        StepExecution(self.flowinstance).execute()
        response = self.client.get(f'/monitoring/flow-instance/{self.flowinstance.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], FlowInstance.Status.SUCCESS)

        response = self.client.get(f'/monitoring/flows/{self.flow.id}/instances/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/monitoring/flows/{self.flow.id}/steps/')
        self.assertEqual(response.status_code, 200)
