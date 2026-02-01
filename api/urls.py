from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("products/", views.ProductAsyncAPIView.as_view()),  # ListAndCreate
    path("products/<int:product_id>/", views.ProductDetailAPIView.as_view()),
    
    path("user-orders/", views.UserOrderListAPIView.as_view(), name="user-orders"),
    
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # path("orders/", views.OrderListAPIView.as_view()),
    # path("products/create", views.ProductCreateAPIView.as_view()), # Create only
    # path("products/info/", views.ProductInfoAPIView.as_view()),
]


router = DefaultRouter()
router.register("order", views.OrderAsyncViewSet, basename="order")
urlpatterns += router.urls
