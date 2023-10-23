# synthetic-monitoring (not final version)

***


# Description

We need a system to test websites

![Structure](https://storage.fileservice.dev/media/0a6e1f3b-19fc-4c0e-81f2-b00407f2a87e.png)

## Infrastructure

- Data storage: SQL Postgres
- API: Python 3.9^, Django 4.0^
- Tests: Django tests
- Other dependencies: redis, celery

System have a docker-compose file which will build all the infrastructure

## Authentication

JWT token authentication

To register you need name, email and password
Upon registration a confirmation email will be sent confirming your email 

You cannot login without email confirmation

You have access only to your test_flows and you can't see or interaction whit flows created by another users 

## How it should work:

1. We send a test name, website base url, the browser in which the test will be run and test scheduler (crontab format)
```json
{
  "name": "Test EBS",
  "url": "https://ebs-integrator.com",
  "browser": "chrome",
  "scheduling": "0 * * * *"
}
```
> What is [crontab format](https://crontab.guru/#0_*_*_*_*)?

2. Then we send the steps that should be performed
```json
[
  {
    "number": 1,
    "action": "click",
    "selector_xpath": "//*[@id=\"homepage\"]/footer/div/div[1]/div/div[2]/div/a"
  },
  {
    "number": 2,
    "action": "tapping",
    "selector_xpath": "//*[@id=\"wpcf7-f2725-o10\"]/form/div[2]/div[1]/div[2]/span[1]/input",
    "content": "Name"
  },
  {
    "number": 3,
    "action": "tapping",
    "selector_xpath": "//*[@id=\"wpcf7-f2725-o10\"]/form/div[2]/div[1]/div[2]/span[2]/input",
    "content": "user@example.com"
  },
  {
    "number": 4,
    "action": "tapping",
    "selector_xpath": "//*[@id=\"wpcf7-f2725-o10\"]/form/div[2]/div[1]/div[2]/span[3]/input",
    "content": "068888888"
  }
]
```
> What is [XPath](https://ro.wikipedia.org/wiki/XPath)?

3. Then we need to activate this test
```json
{
  "active": true 
}
```

4. After all this test you have to run after the set scheduler and save execution logs at each run and step

> The log should also contain screenshot of the browser on current step

> What is [Selenium](https://www.selenium.dev)?

5. We need some endpoint to see all execution logs 
6. We need some endpoint to instant run of test (when this be called test start instantly)
7. When some test has failed we need to receive a notification whit step details (use a django_templates)


### Useful links:
- [Django](https://docs.djangoproject.com/en/4.0/)
- [Django Rest Framework](https://www.django-rest-framework.org)
- [Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
- [Selenium](https://www.selenium.dev)
