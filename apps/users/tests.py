import json
import re

import django
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from django.core import mail


class TestUser(APITestCase):
    def test_register(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "finicacr7@gmail.com",
            "password": "string",
        }
        response = self.client.post('/users/register/', data=data, format='json')
        count = User.objects.all().filter(email=data['email']).count()
        self.assertEqual(count, 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm email')

    def test_bad_register(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "dasdsa",
            "password": "string",
        }
        response = self.client.post('/users/register/', data=data, format='json')
        count = User.objects.all().filter(email=data['email']).count()

        self.assertEqual(count, 0)
        self.assertEqual(mail.outbox, [])

    def test_activation(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "finicacr7@gmail.com",
            "password": "string",
        }
        response = self.client.post('/users/register/', data=data, format='json')
        activation_url = mail.outbox[0].body
        response = self.client.get(activation_url, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bad_activation(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "finicacr7@gmail.com",
            "password": "string",
        }
        response = self.client.post('/users/register/', data=data, format='json')
        activation_url = mail.outbox[0].body + "bad"
        response = self.client.get(activation_url, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_generate_token(self):
        self.test_register()

        user = User.objects.first()
        token = default_token_generator.make_token(user)
        response = self.client.get(f'/users/activate?user_id={user.id}&confirmation_token={token}', follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bad_activate_generate_token(self):
        self.test_register()

        user = User.objects.first()
        token = default_token_generator.make_token(user)
        response = self.client.get(f'/users/activate?user_id={user.id}&confirmation_token={token}bad', follow=True)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "finicacr7@gmail.com",
            "password": "string",
        }

        user = User.objects.create(**data)
        user.is_confirmed = True
        user.save()

        response = self.client.post(
            '/users/login/',
            data=json.dumps({
                'email': 'finicacr7@gmail.com',
                'password': 'string'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bad_login(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "finicacr7@gmail.com",
            "password": "string",
        }

        user = User.objects.create(**data)
        user.is_confirmed = False
        user.save()

        response = self.client.post(
            '/users/login/',
            data=json.dumps({
                'email': 'finicacr7@gmail.com',
                'password': 'string'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
