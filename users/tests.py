import base64

from rest_framework import status, HTTP_HEADER_ENCODING
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User

from users.models import Employee, Driver, Relationship, Dispatcher


def authenticate():
    username = 'olegshek23'
    password = '123456789'
    email = 'oleg@gmail.com'
    User.objects.create_superuser(username=username, password=password, email=email)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Basic ' + base64.b64encode(
            '{}:{}'.format(username, password).encode(HTTP_HEADER_ENCODING)).decode())
    return client


class TestEndpoints(APITestCase):
    fixtures = ['users',
                'employees',
                'dispatchers',
                'drivers',
                'relationship']
    dispatcher_url = '/dispatchers/'
    drivers_url = '/drivers/'
    relationships_url = '/relationships/'

    def test_get_dispatchers(self):
        self.client = authenticate()
        response = self.client.get(self.dispatcher_url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_drivers(self):
        self.client = authenticate()
        response = self.client.get(self.dispatcher_url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_relationships(self):
        self.client = authenticate()
        response = self.client.get(self.dispatcher_url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class CreationTests(APITestCase):
    fixtures = ['users',
                'employees',
                'dispatchers',
                'drivers',
                'relationship']
    dispatcher_url = '/dispatchers/'
    drivers_url = '/drivers/'
    relationships_url = '/relationships/'

    def test_create_dispatcher(self):
        self.client = authenticate()
        user = User.objects.get(username='user').id
        data = {'user': user}
        response = self.client.post(self.dispatcher_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_driver(self):
        self.client = authenticate()
        user = User.objects.get(username='user').id
        data = {'user': user}
        response = self.client.post(self.drivers_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_relationship(self):
        self.client = authenticate()
        senior = Dispatcher.objects.get(user=User.objects.get(username='admin')).id
        leg = Dispatcher.objects.get(user=User.objects.get(username='dispatcher3')).id
        data = {'senior_dispatcher': senior, 'leg': leg}
        response = self.client.post(self.relationships_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_relationship_with_self(self):
        self.client = authenticate()
        senior = Dispatcher.objects.get(user=User.objects.get(username='admin')).id
        leg = Dispatcher.objects.get(user=User.objects.get(username='admin')).id
        data = {'senior_dispatcher': senior, 'leg': leg}
        response = self.client.post(self.relationships_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


