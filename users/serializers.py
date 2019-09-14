from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Dispatcher, Driver, Relationship


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username']


class DispatcherSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Dispatcher
        fields = ['user',
                  'legs',
                  'legs_choice_for_90',
                  'legs_choice_for_80',
                  'legs_choice_for_70',
                  'calc_gross',
                  'calc_drivers_gross_percentage',
                  'calc_sum_gross_percentage',
                  'calc_reward_from_drivers',
                  'calc_reward_from_legs']


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Driver
        fields = ['user',
                  'monitor_dispatcher',
                  'gross',
                  'plan_gross',
                  'reward_percentage',
                  'calc_gross_percentage',
                  'calc_reward_from_driver']


class RelationshipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Relationship
        fields = ['url',
                  'senior_dispatcher',
                  'leg',
                  'reward_percentage',
                  'calc_reward_from_leg']
