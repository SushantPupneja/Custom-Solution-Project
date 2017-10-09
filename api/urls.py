from django.conf.urls import url
from .views import CustomTracker, get_devices , BeaconAllocation

urlpatterns = [
    url(r'^api/customtracker', CustomTracker , name="CustomTracker"),
    url(r'^api/getDevices', get_devices , name="CustomTracker"),
    # url(r'^api/beaconstatus', StatusConfiguration , name="StatusConfiguration"),
    url(r'^api/beaconallocation', BeaconAllocation , name="BeaconAllocation"),
]