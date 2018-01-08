# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from room_booking.forms import ConfirmBookingForm
from room_booking.models import Room, Booking


class RoomBookingAppTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("user-1")
        self.user1.set_password('qwerty11')
        self.user1.save()

        self.room1 = Room.objects.create(price=100)

        start_date = datetime.datetime.today() + datetime.timedelta(days=20)
        end_date = datetime.datetime.today() + datetime.timedelta(days=15)
        self.booking1 = Booking.objects.create(room=self.room1, owner=self.user1,
                                               start_date=start_date, end_date=end_date,
                                               credit_card="45909-901-6584-3200")

    def test_room_list_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["room_list"].count(), 0)

    def test_room_available_wrong_date(self):
        end_date = datetime.datetime.today() - datetime.timedelta(days=1)
        response = self.client.get('/',
                                   {'start_date': datetime.datetime.today().strftime("%Y-%m-%d"),
                                    'end_date': end_date.strftime("%Y-%m-%d"),
                                    'amount_people': 1})

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "error")
        self.assertTrue("End date should be greater than start date." in message.message)

    def test_room_available_list(self):
        response = self.client.get('/',
                                   {'start_date': datetime.datetime.today().strftime("%Y-%m-%d"),
                                    'end_date': datetime.datetime.today().strftime("%Y-%m-%d"),
                                    'amount_people': 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["room_list"].count(), 1)

    def test_booking_list_view(self):
        self.client.login(username='user-1', password='qwerty11')
        response = self.client.get(reverse('booking-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["booking_list"].count(), 1)

    def test_booking_detail_view(self):
        self.client.login(username='user-1', password='qwerty11')
        response = self.client.get(reverse('booking-detail', args={self.booking1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking'].id, 1)

    def test_confirm_booking_view(self):
        self.client.login(username='user-1', password='qwerty11')
        start_date = datetime.datetime.today() + datetime.timedelta(days=50)
        end_date = datetime.datetime.today() + datetime.timedelta(days=60)
        response = self.client.get(reverse('confirm-booking', kwargs={'pk': self.room1.id,
                                                                      'start_date': start_date.strftime(
                                                                          "%Y-%m-%d"),
                                                                      'end_date': end_date.strftime(
                                                                          "%Y-%m-%d"),
                                                                      'amount_people': 1,
                                                                      'total_booking_days': 10}))
        self.assertEqual(response.status_code, 200)


class ConfirmBookingFomTests(TestCase):
    def test_invalid_data(self):
        form = ConfirmBookingForm({
            'notes': "I want coffee",
        }, )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'credit_card': ['This field is required.'],
        })

    def test_valid_data(self):
        form = ConfirmBookingForm({
            'credit_card': "4567-5462-134-4562",
        }, )
        self.assertTrue(form.is_valid())
