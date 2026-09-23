from django.urls import path

from .views import ProxyStatusView


urlpatterns = [
    path(
        "status/",
        ProxyStatusView.as_view(),
        name="proxy-status",
    ),
]