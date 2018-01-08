from django.conf.urls import url

from views import *

urlpatterns = [
    url(r'^$', RoomList.as_view(), name='room-list'),
    url(r'^confirm-booking/(?P<pk>\d+)/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{'
        r'2}-\d{2})/(?P<amount_people>\d+)/(?P<total_booking_days>\d+)/$', ConfirmBooking.as_view(),
        name='confirm-booking'),
    url(r'^booking-list/$', BookingList.as_view(), name='booking-list'),
    url(r'^booking-detail/(?P<pk>\d+)/$', BookingDetail.as_view(), name='booking-detail'),

    url(r'^download-booking-pdf/(?P<pk>\d+)/$', BookingPdf.as_view(), name='download-booking-pdf'),

]
