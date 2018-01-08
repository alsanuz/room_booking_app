# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from models import Booking, Room


class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'price', 'max_people_allowed')


admin.site.register(Room, RoomAdmin)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'start_date', 'end_date', 'price', 'amount_people')


admin.site.register(Booking, BookingAdmin)
