from django.urls import path

from .views import InstrumentListView,LatestTickView


urlpatterns = [
    path(
        "instruments/",
        InstrumentListView.as_view(),
        name="instrument-list",
    ),
    path(
        "ticks/<str:security_id>/",
        LatestTickView.as_view(),
        name="latest-tick",
    ),
]