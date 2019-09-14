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

    @property
    def calc_gross(self):
        legs = Relationship.objects.filter(senior_dispatcher=self).values_list('leg')
        legs = Dispatcher.objects.all().filter(pk__in=legs)
        self.gross = sum(
            [driver.calc_gross for driver in Driver.objects.filter(monitor_dispatcher=self, gross__isnull=False)]) + \
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

    # @property
    # def calc_reward(self):


class Driver(Employee):
    monitor_dispatcher = models.ForeignKey(Dispatcher, null=True, on_delete=models.SET_NULL, related_name='monitor')
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


class Relationship(models.Model):
    senior_dispatcher = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='senior')
    leg = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='leg')
    reward_percentage = models.FloatField(validators=[MinValueValidator(0.0),
                                                      MaxValueValidator(100)],
                                          null=True,
                                          default=0.0)
