# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from room_booking.forms import ConfirmBookingForm
from room_booking.models import Booking
from room_booking.models import Room
from room_booking_project.extras.mixins import ProtectedView


class RoomList(ListView):
    """
    Show available room list between two dates and amount people

    """
    model = Room
    queryset = Room.objects.all()

    def get_queryset(self):
        start_date = self.request.GET.get("start_date", None)
        end_date = self.request.GET.get("end_date", None)
        amount_people = self.request.GET.get("amount_people", None)

        # Validate that dates are correct
        if end_date < start_date:
            messages.error(self.request, 'End date should be greater than start date.')
            return self.queryset.none()

        if start_date and end_date and amount_people:
            # Exclude unavailable rooms
            exclude_room_ids = Booking.objects.filter(Q(start_date__range=(start_date, end_date)) |
                                                      Q(end_date__range=(start_date,
                                                                         end_date))).values_list(
                'room', flat=True)
            queryset = self.queryset.exclude(booking__room__in=exclude_room_ids).filter(
                max_people_allowed__gte=amount_people)

            return queryset

        return self.queryset.none()

    def get_context_data(self, **kwargs):
        context = super(RoomList, self).get_context_data(**kwargs)
        start_date = self.request.GET.get("start_date", None)
        end_date = self.request.GET.get("end_date", None)
        if start_date and end_date:
            context['total_booking_days'] = (datetime.strptime(end_date, "%Y-%m-%d") -
                                             datetime.strptime(start_date, "%Y-%m-%d")).days

        return context


class ConfirmBooking(ProtectedView, CreateView):
    """
    Confirm booking for an available room

    """
    model = Booking
    form_class = ConfirmBookingForm
    template_name = "room_booking/confirm_booking_form.html"
    success_url = reverse_lazy('booking-list')

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.owner = self.request.user
        booking.room_id = int(self.kwargs['pk'])
        booking.start_date = datetime.strptime(self.kwargs['start_date'], "%Y-%m-%d").date()
        booking.end_date = datetime.strptime(self.kwargs['end_date'], "%Y-%m-%d").date()
        booking.amount_people = self.kwargs['amount_people']
        booking.save()

        # Flash success message
        messages.add_message(self.request, messages.SUCCESS, "Booking done successfully")
        return super(ConfirmBooking, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ConfirmBooking, self).get_context_data(**kwargs)
        context['start_date'] = self.kwargs['start_date']
        context['end_date'] = self.kwargs['end_date']
        context['amount_people'] = self.kwargs['amount_people']
        context['total_booking_days'] = self.kwargs['total_booking_days']

        room = get_object_or_404(Room, pk=self.kwargs['pk'])
        context['room'] = room
        context['total_booking_price'] = room.price * int(self.kwargs['total_booking_days'])
        return context


class BookingList(ProtectedView, ListView):
    """
    Show all logged user bookings

    """
    model = Booking
    queryset = Booking.objects.none()

    def get_queryset(self):
        return Booking.objects.filter(owner=self.request.user)


class BookingDetail(ProtectedView, DetailView):
    """
    Show detail info about a booking

    """
    model = Booking


class BookingPdf(ProtectedView, View):
    """
    Create a pdf with all booking information

    """

    def get(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])

        response = HttpResponse(content_type='application/pdf')
        filename = "Booking - %s.pdf" % booking.id
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        pdf = canvas.Canvas(response, pagesize=A4)
        self.header(pdf, booking)
        self.body(pdf, booking)
        pdf.showPage()
        pdf.save()

        return response

    def header(self, pdf, booking):
        title = _("Booking - %s" % booking.id)
        subtitle = _("Here you have all information about your booking")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(250, 790, title)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(180, 760, subtitle)

    def body(self, pdf, booking):
        table_content = [(field.name.capitalize().replace("_", " "), getattr(booking, field.name))
                         for field in booking._meta.get_fields() if field.name != 'id']
        table = Table(table_content, colWidths=[7 * cm, 7 * cm])

        # Setting table style
        table.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))

        table.wrapOn(pdf, 800, 600)
        table.drawOn(pdf, 100, 550)
