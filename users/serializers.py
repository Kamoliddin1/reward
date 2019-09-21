from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from users.models import Dispatcher, Driver, Relationship


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username']


class DispatcherSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Dispatcher
        fields = ['user',
                  'legs',
                  'legs_choice_for_90',
                  'legs_choice_for_80',
                  'legs_choice_for_70',
                  'gross',
                  'drivers_gross',
                  'legs_gross',
                  'plan_gross',
                  'gross_percentage',
                  'reward']


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Driver
        fields = ['user',
                  'monitor_dispatcher',
                  'gross',
                  'plan_gross']


class RelationshipSerializer(serializers.HyperlinkedModelSerializer):
    senior_dispatcher = serializers.PrimaryKeyRelatedField(queryset=Dispatcher.objects.all())
    leg = serializers.PrimaryKeyRelatedField(queryset=Dispatcher.objects.all())

    class Meta:
        model = Relationship
        fields = ['url',
                  'senior_dispatcher',
                  'leg',
                  'reward']

    def validate(self, attrs):
        if attrs.get('senior_dispatcher') == attrs.get('leg'):
            raise ValidationError(detail='Cannot create relationship with self')
        return super().validate(attrs)
