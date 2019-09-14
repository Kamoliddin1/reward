# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from users.models import Dispatcher, Driver, Relationship

admin.site.register(Dispatcher)
admin.site.register(Driver)
admin.site.register(Relationship)