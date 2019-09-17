from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from django.db.utils import IntegrityError


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gross = models.IntegerField(default=0)
    plan_gross = models.IntegerField(default=0)
    gross_percentage = models.FloatField(default=0.0)


class Dispatcher(Employee):
    legs = models.ManyToManyField('self', through='Relationship', symmetrical=False)
    drivers_gross = models.IntegerField(default=0)
    legs_gross = models.IntegerField(default=0)
    legs_choice_for_90 = models.IntegerField(default=0)
    legs_choice_for_80 = models.IntegerField(default=0)
    legs_choice_for_70 = models.IntegerField(default=0)

    def calc_plan_gross(self):
        try:
            self.plan_gross = sum([Driver.objects.filter(
                monitor_dispatcher=self, plan_gross__isnull=False).aggregate(
                Sum('plan_gross'))['plan_gross__sum'],
                                   Relationship.objects.filter(
                                       senior_dispatcher=self).aggregate(
                                       Sum('leg__driver__plan_gross'))['leg__driver__plan_gross__sum']])
            self.save(update_fields=['plan_gross'])
            return self.plan_gross
        except IntegrityError:
            self.plan_gross = 0
            self.save(update_fields=['plan_gross'])
            return self.plan_gross

    def calc_drivers_gross(self):
        try:
            self.drivers_gross = Driver.objects.filter(
                monitor_dispatcher=self, gross__isnull=False).aggregate(
                Sum('gross'))['gross__sum']
            self.save(update_fields=['drivers_gross'])
            return self.drivers_gross
        except IntegrityError:
            self.drivers_gross = 0
            self.save(update_fields=['drivers_gross'])
            return self.drivers_gross

    def calc_legs_gross(self):
        try:
            self.legs_gross = Relationship.objects.filter(
                senior_dispatcher=self).aggregate(
                Sum('leg__drivers_gross'))['leg__drivers_gross__sum']
            self.save(update_fields=['legs_gross'])
            return self.legs_gross
        except IntegrityError:
            self.legs_gross = 0
            self.save(update_fields=['drivers_gross'])
            return self.legs_gross

    def calc_gross(self):
        self.gross = Dispatcher.objects.filter(
            pk=self.pk).aggregate(
            gross_sum=Sum('drivers_gross') + Sum('legs_gross'))['gross_sum']
        self.save(update_fields=['gross'])
        return self.gross

    def calc_gross_percentage(self):
        try:
            self.gross_percentage = self.gross / self.plan_gross * 100
            self.save(update_fields=['gross_percentage'])
        except ZeroDivisionError:
            return 0

    @property
    def calc_sum_reward(self):
        self.reward = sum([driver.calc_reward_from_driver for driver in
                           Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)] +
                          [leg.calc_reward_from_leg for leg in Relationship.objects.filter(senior_dispatcher=self)])
        self.save()
        return self.reward

    @property
    def calc_reward_from_drivers(self):
        drivers_reward = sum([driver.calc_gross_percentage for driver in
                              Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)])
        return drivers_reward

    @property
    def calc_reward_from_legs(self):
        leg_reward_list = [leg.calc_reward_from_leg for leg in Relationship.objects.filter(senior_dispatcher=self)]

        if self.gross_percentage == 100:
            return self.calc_sum_reward
        elif 90 <= self.gross_percentage <= 99:
            return sum(leg_reward_list[:self.legs_choice_for_90])
        elif 80 <= self.gross_percentage <= 89:
            return sum(leg_reward_list[:self.legs_choice_for_80])
        elif 70 <= self.gross_percentage <= 79:
            return sum(leg_reward_list[:self.legs_choice_for_70])
        elif 60 <= self.gross_percentage <= 69:
            return self.calc_reward_from_drivers
        else:
            return 0


class Driver(Employee):
    monitor_dispatcher = models.ForeignKey(Dispatcher, null=True,
                                           on_delete=models.SET_NULL)
    reward_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                                      MaxValueValidator(100)],
                                          null=True,
                                          default=0.0)

    def calc_gross_percentage(self):
        try:
            self.gross_percentage = self.gross / self.plan_gross * 100
            self.save(update_fields=['gross_percentage'])
        except ZeroDivisionError:
            return 0

    @property
    def calc_reward_from_driver(self):
        return self.gross * self.reward_percentage


class Relationship(models.Model):
    senior_dispatcher = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='senior')
    leg = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='leg')
    reward_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                                      MaxValueValidator(1.0)],
                                          null=True,
                                          default=0.0)

    @property
    def calc_reward_from_leg(self):
        return self.leg.calc_gross * self.reward_percentage
