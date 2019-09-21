from django.db import models
from django.db.models import OuterRef, FloatField
from django.db.models.expressions import Subquery


class SumSubquery(Subquery):
    template = '(SELECT SUM(dgs.plan_gross) FROM (%(subquery)s) as dgs)'
    output_field = FloatField()

class GrossSumSubquery(Subquery):
    template = '(SELECT SUM(dgs.gross) FROM (%(subquery)s) as dgs)'
    output_field = FloatField()


class DispatcherQueryset(models.QuerySet):
    def add_drivers_plan_gross(self):
        from users.models import Driver
        return self.annotate(
            driver_plan_gross=SumSubquery(
                queryset=Driver.objects.filter(monitor_dispatcher_id=OuterRef('id')).values('plan_gross'),
                output_field=FloatField()
            )
        )


    def add_drivers_gross(self):
        from users.models import Driver
        return self.annotate(
            driver_gross=GrossSumSubquery(
                queryset=Driver.objects.filter(monitor_dispatcher_id=OuterRef('id')).values('gross'),
                output_field=FloatField()
            )
        )


