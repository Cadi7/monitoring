from datetime import datetime
from time import sleep

import cloudinary
import cloudinary.uploader
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

import config.settings
from apps.monitoring.models import Step, Flow, FlowInstance, Logs
from config.settings import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_SECRET_KEY


class StepExecution:

    def __init__(self, flowinstance):
        self._driver = None
        self.url = flowinstance.url
        self.browser = flowinstance.browser
        self.flowinstance = flowinstance
        self.steps = Step.objects.filter(flow=self.flowinstance.test)

    @staticmethod
    def init_driver(options):
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        options.add_argument('--verbose')
        options.add_argument('--whitelisted-ips=')
        options.add_argument('--window-size=1920,1080')
        return webdriver.Remote(config.settings.SELENIUM_HUB_URL, options.to_capabilities())

    @property
    def driver(self):
        if not getattr(self, '_driver'):
            options_mapping = {
                Flow.BrowserInstance.CHROME: webdriver.ChromeOptions,
                Flow.BrowserInstance.FIREFOX: webdriver.FirefoxOptions,
            }
            options = options_mapping[self.browser]()
            self._driver = self.init_driver(options)
        return self._driver

    def click(self, step):
        self.driver.find_element(By.XPATH, step.selector_xpath).click()

    def tapping(self, step):
        self.driver.find_element(By.XPATH, step.selector_xpath).send_keys(step.content)

    def submit(self, step):
        self.driver.find_element(By.XPATH, step.selector_xpath).submit()

    def clear(self, step):
        self.driver.find_element(By.XPATH, step.selector_xpath).clear()

    def enter(self, step):
        self.driver.find_element(By.XPATH, step.selector_xpath).send_keys(Keys.ENTER)

    def action(self, step):
        func = getattr(self, step.action, None)
        if not func:
            raise NotImplementedError(f"Action {step.action} not implemented")
        return func(step)

    @staticmethod
    def cloudinary_setup():
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_SECRET_KEY,
            cloud_url=CLOUDINARY_CLOUD_NAME
        )

    def verify_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
            return True
        except Exception:
            return False

    def makescreenshot(self, filename):
        img = self.driver.get_screenshot_as_png()
        with open(filename, 'wb') as f:
            f.write(img)

    def upload_to_cloudinary(self, file_name):
        self.cloudinary_setup()
        return cloudinary.uploader.upload(file_name, use_filename=True)['url']

    def make_screend_geturl(self):
        file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.png'
        self.makescreenshot(file_name)
        url = self.upload_to_cloudinary(file_name)
        return url

    def highlight(self, xpath, active=True):
        if self.verify_xpath(xpath) & active:
            self.driver.execute_script("arguments[0].style.border='3px solid red'", self.driver.find_element(By.XPATH, xpath))
            sleep(1)
        else:
            self.driver.execute_script("arguments[0].style.border=''", self.driver.find_element(By.XPATH, xpath))




    def execute(self):
        self.driver.get(self.url)
        self.flowinstance.status = FlowInstance.Status.IN_PROGRESS

        for step_number in range(1, len(self.steps) + 1):
            try:
                step = self.steps.get(step_number=step_number)
                self.highlight(step.selector_xpath, active=True)
                Logs.objects.create(step=step, attachment=self.make_screend_geturl(), status=Logs.Status.SUCCESS,
                                    additional_data={}, flow_instance=self.flowinstance)
                self.action(step)
                self.highlight(step.selector_xpath, active=False)
                sleep(5)
                self.flowinstance.status = FlowInstance.Status.SUCCESS
                self.flowinstance.save(update_fields=['status'])
            except Exception as e:
                Logs.objects.create(step=step, attachment=self.make_screend_geturl(), status=Logs.Status.FAIL,
                                    additional_data=str(e), flow_instance=self.flowinstance)
                self.flowinstance.status = FlowInstance.Status.FAIL
                self.flowinstance.save(update_fields=['status'])
                return
        Logs.objects.create(step=step, attachment=self.make_screend_geturl(), status=Logs.Status.FINAL,
                                additional_data={}, flow_instance=self.flowinstance)
        print("Done " + self.flowinstance.url)
