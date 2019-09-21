from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce

from users.querysets import DispatcherQueryset


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Dispatcher(Employee):
    legs = models.ManyToManyField('self', through='Relationship', symmetrical=False)
    legs_choice_for_90 = models.IntegerField(default=0)
    legs_choice_for_80 = models.IntegerField(default=0)
    legs_choice_for_70 = models.IntegerField(default=0)
    reward_percentage_for_drivers = models.FloatField(validators=[MinValueValidator(0.0),
                                                                  MaxValueValidator(1.0)],
                                                      null=True,
                                                      default=0.0)
    reward_percentage_for_legs = models.FloatField(validators=[MinValueValidator(0.0),
                                                               MaxValueValidator(1.0)],
                                                   null=True,
                                                   default=0.0)

    objects = DispatcherQueryset.as_manager()

    def get_driver_model(self):
        return apps.get_model('users', 'Driver')

    def get_relationship_model(self):
        return apps.get_model('users', 'Relationship')

    @property
    def drivers_plan_gross(self):
        plan = Dispatcher.objects. \
            add_drivers_plan_gross(). \
            get(pk=self.pk).driver_plan_gross
        if plan is None:
            return 0.0
        else:
            return plan

    @property
    def legs_plan_gross(self):
        return Dispatcher.objects. \
            filter(pk__in=self.get_relationship_model(). \
                   objects.filter(senior_dispatcher=self). \
                   values_list('leg', flat=True)). \
            add_drivers_plan_gross(). \
            aggregate(legs_driver_plan_gross_sum=Coalesce(Sum('driver_plan_gross'), 0))['legs_driver_plan_gross_sum']

    @property
    def plan_gross(self):
        return self.drivers_plan_gross + self.legs_plan_gross

    @property
    def drivers_gross(self):
        gross = Dispatcher.objects. \
            add_drivers_gross(). \
            get(pk=self.pk). \
            driver_gross
        if gross is None:
            return 0
        else:
            return gross

    @property
    def legs_gross(self):
        return Dispatcher.objects. \
            filter(pk__in=self.get_relationship_model(). \
                   objects.filter(senior_dispatcher=self). \
                   values_list('leg', flat=True)). \
            add_drivers_gross(). \
            aggregate(legs_driver_gross_sum=Coalesce(Sum('driver_gross'), 0))['legs_driver_gross_sum']

    @property
    def gross(self):
        return self.drivers_gross + self.legs_gross

    @property
    def gross_percentage(self):
        try:
            return self.gross / self.plan_gross * 100
        except ZeroDivisionError:
            return 0

    @property
    def reward_from_drivers(self):
        return self.drivers_gross * self.reward_percentage_for_drivers

    @property
    def reward_from_legs(self):
        return self.legs_gross * self.reward_percentage_for_legs

    @property
    def sum_reward(self):
        return self.reward_from_legs * self.reward_from_drivers

    @property
    def reward(self):
        leg_reward_list = [leg.calc_reward_from_leg for leg in Relationship.objects.filter(senior_dispatcher=self)]

        if self.gross_percentage == 100:
            return self.sum_reward
        elif 90 <= self.gross_percentage <= 99:
            return sum(leg_reward_list[:self.legs_choice_for_90])
        elif 80 <= self.gross_percentage <= 89:
            return sum(leg_reward_list[:self.legs_choice_for_80])
        elif 70 <= self.gross_percentage <= 79:
            return sum(leg_reward_list[:self.legs_choice_for_70])
        elif 60 <= self.gross_percentage <= 69:
            return self.reward_from_drivers
        else:
            return 0


class Driver(Employee):
    gross = models.FloatField(default=0.0)
    plan_gross = models.FloatField(default=0.0)
    monitor_dispatcher = models.ForeignKey(Dispatcher, null=True,
                                           on_delete=models.PROTECT)


class Relationship(models.Model):
    senior_dispatcher = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='senior')
    leg = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='leg')
