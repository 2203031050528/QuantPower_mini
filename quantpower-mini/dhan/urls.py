from django.urls import path

from .views import DhanAccountView


urlpatterns = [
    path(
        "account/",
        DhanAccountView.as_view(),
        name="dhan-account"
    ),
]