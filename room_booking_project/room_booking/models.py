# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _

STANDARD_ROOM = 'standard'
FAMILY_ROOM = 'family'
SUITE_ROOM = 'suite'

TYPE_ROOM = (
    (STANDARD_ROOM, 'Standard'), (FAMILY_ROOM, 'Family'), (SUITE_ROOM, 'Suite'),
)


class Room(models.Model):
    type = models.CharField(max_length=8, choices=TYPE_ROOM, default=STANDARD_ROOM)
    price = models.FloatField(help_text=_("Price per night in Euros"))
    max_people_allowed = models.IntegerField(default=1)
    image = models.ImageField(null=True, blank=True, upload_to='room-images/')
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "Room(%s) - %s(%s)" % (self.pk, self.type, self.price)


class Booking(models.Model):
    room = models.ForeignKey(Room)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    start_date = models.DateField()
    end_date = models.DateField()
    credit_card = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True, help_text=_('User wishes'))
    locator = models.CharField(max_length=250, help_text=_("Booking locator"), blank=True)
    price = models.FloatField(help_text=_("Total booking price"), blank=True)
    amount_people = models.IntegerField(default=1)

    def __unicode__(self):
        return "Booking(%s) - (%s - %s)" % (self.pk, self.start_date, self.end_date)

    def save(self, *args, **kwargs):
        # Generate a unique locator for each booking
        self.locator = self._get_unique_locator(self.start_date, self.owner)
        # Calculate total booking price
        self.price = self.calc_total_price()
        super(Booking, self).save(*args, **kwargs)

    def calc_total_price(self):
        return (self.end_date - self.start_date).days * self.room.price

    @staticmethod
    def _get_unique_locator(date, user):
        return get_random_string(length=8) + date.strftime("%Y%m%d") + str(user.pk)
