import base64

from rest_framework import status, HTTP_HEADER_ENCODING
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User


def authenticate():
    username = 'olegshek23'
    password = '123456789'
    email = 'oleg@gmail.com'
    User.objects.create_user(username=username, password=password, email=email)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Basic ' + base64.b64encode(
            '{}:{}'.format(username, password).encode(HTTP_HEADER_ENCODING)).decode())
    return client
