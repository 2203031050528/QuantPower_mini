from django.urls import path

from .views import (
    OrderCreateView,
    OrderListView,
    PositionListView,
    DhanOrderPreviewView,
)


urlpatterns = [

    path(
        "",
        OrderListView.as_view(),
        name="order-list",
    ),

    path(
        "create/",
        OrderCreateView.as_view(),
        name="order-create",
    ),

    path(
        "positions/",
        PositionListView.as_view(),
        name="position-list",
    ),
    path(
    "dhan/preview/",
    DhanOrderPreviewView.as_view(),
    name="dhan-order-preview",
),
]