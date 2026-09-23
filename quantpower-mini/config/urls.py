from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/dhan/",
        include("dhan.urls")
    ),
     path(
        "api/auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path(
        "api/market/",
        include("market.urls")
    ),
    path(
        "api/orders/",
        include("orders.urls")
    ),
    path(
    "api/proxy/",
    include("proxy.urls"),
),

]
