from django import forms

from room_booking.models import Booking


class ConfirmBookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['credit_card', 'notes']

    def __init__(self, *args, **kwargs):
        super(ConfirmBookingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
