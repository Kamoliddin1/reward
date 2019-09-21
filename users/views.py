from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from users.models import Dispatcher, Driver, Relationship
from users.serializers import UserSerializer, DispatcherSerializer, DriverSerializer, RelationshipSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class DispatcherViewSet(viewsets.ModelViewSet):
    queryset = Dispatcher.objects.all()
    serializer_class = DispatcherSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.add_drivers_plan_gross()
        queryset = queryset.add_drivers_gross()
        return queryset



class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAdminUser]


class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    permission_classes = [permissions.IsAdminUser]


