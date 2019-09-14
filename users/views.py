# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from users.models import Dispatcher


def calc_gross_of_first_dispatchers(request):
    dispatcher = Dispatcher.objects.first()
    gross = dispatcher.calc_gross
    return JsonResponse({'gross': gross})
