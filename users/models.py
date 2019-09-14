from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gross = models.IntegerField(null=True)
    plan_gross = models.IntegerField(null=True)

    @property
    def calc_gross(self):
        return self.gross


class Dispatcher(Employee):
    legs = models.ManyToManyField('self', through='Relationship', symmetrical=False)
    legs_choice_for_90 = models.IntegerField(null=True)
    legs_choice_for_80 = models.IntegerField(null=True)
    legs_choice_for_70 = models.IntegerField(null=True)


    @property
    def calc_gross(self):
        legs = Relationship.objects.filter(senior_dispatcher=self).values_list('leg')
        legs = Dispatcher.objects.all().filter(pk__in=legs)
        self.gross = sum(
            [driver.calc_gross for driver in Driver.objects.filter(monitor_dispatcher=self,
                                                                   gross__isnull=False)]) + \
                     sum([leg.calc_gross for leg in legs])
        self.save()
        return self.gross

    @property
    def calc_drivers_gross_percentage(self):
        self.gross_list = [
            driver.calc_gross_percentage for driver in
            Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)
        ]
        try:
            self.drivers_gross_percentage = sum(self.gross_list) / len(self.gross_list)
        except ZeroDivisionError:
            return 0
        self.save()
        return self.drivers_gross_percentage

    @property
    def calc_sum_gross_percentage(self):
        legs = Relationship.objects.filter(senior_dispatcher=self).values_list('leg')
        legs = Dispatcher.objects.all().filter(pk__in=legs)
        self.gross_list = [driver.calc_gross_percentage for driver in
                           Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)] + \
                          [leg.calc_drivers_gross_percentage for leg in legs]
        self.gross_percentage = sum(self.gross_list) / len(self.gross_list)
        self.save()
        return self.gross_percentage

    @property
    def calc_reward(self):
        self.reward = sum([driver.calc_reward_from_driver for driver in
                           Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)] +
                          [leg.calc_reward_from_leg for leg in Relationship.objects.filter(senior_dispatcher=self)])
        self.save()
        return self.reward

    @property
    def calc_reward_from_drivers(self):
        self.drivers_reward = sum([driver.calc_gross_percentage for driver in
                                   Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)])
        return self.drivers_reward


    @property
    def calc_reward_from_legs(self):
        leg_reward_list = [leg.calc_reward_from_leg for leg in Relationship.objects.filter(senior_dispatcher=self)]

        if self.calc_sum_gross_percentage == 100:
            return self.calc_reward
        elif 90 <= self.calc_sum_gross_percentage <= 99:
            return sum(leg_reward_list[:self.legs_choice_for_90])
        elif 80 <= self.calc_sum_gross_percentage <= 89:
            return sum(leg_reward_list[:self.legs_choice_for_80])
        elif 70 <= self.calc_sum_gross_percentage <= 79:
            return sum(leg_reward_list[:self.legs_choice_for_70])
        elif 60 <= self.calc_sum_gross_percentage <= 69:
            return self.calc_reward_from_drivers
        else:
            return None


class Driver(Employee):
    monitor_dispatcher = models.ForeignKey(Dispatcher, null=True,
                                           on_delete=models.SET_NULL,
                                           related_name='monitor')
    reward_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                                      MaxValueValidator(100)],
                                          null=True,
                                          default=0.0)

    @property
    def calc_gross_percentage(self):
        try:
            return self.gross / self.plan_gross * 100
        except ZeroDivisionError:
            return 0

    @property
    def calc_reward_from_driver(self):
        return self.gross * self.reward_percentage


class Relationship(models.Model):
    senior_dispatcher = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='senior')
    leg = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='leg')
    reward_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                                      MaxValueValidator(100)],
                                          null=True,
                                          default=0.0)

    @property
    def calc_reward_from_leg(self):
        return self.leg.calc_gross * self.reward_percentage
