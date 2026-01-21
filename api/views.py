from django.db.models import Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from api.filters import InStockFilterBackend, ProductFilter, OrderFilter
from api.models import Order, OrderItem, Product
from api.serializers import (
    OrderSerializer,
    ProductInfoSerializer,
    ProductSerializer,
    OrderCreateSerializer,
)


class ProductListAPIView(generics.ListCreateAPIView):
    # queryset = Product.objects.all()
    queryset = Product.objects.order_by("pk")  # for paginatiion yield warning
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "stock"]
    # pagination_class = PageNumberPagination
    # pagination_class.page_size = 2
    # pagination_class.page_query_param = 'pagenum'
    # pagination_class.page_size_query_param = 'size'
    # pagination_class.max_page_size = 4
    pagination_class = LimitOffsetPagination

    # @method_decorator(cache_page(60 * 15 ,key_prefix='product_list'))
    # def list(self,request , *args, **kwargs):
    #     return super().list(request,*args,**kwargs)

    # def get_queryset(self):
    #     import time
    #     time.sleep(2)
    #     return super().get_queryset()

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


# class ProductCreateAPIView(generics.CreateAPIView):
#     model = Product
#     serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = "product_id"


class OrderViewSet(viewsets.ModelViewSet):
    # throttle_scope  = 'orders'
    queryset = Order.objects.prefetch_related("items__product")
    # OrderCreateSerializer
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return super().get_serializer_class()

    # 1
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)

        return qs

    # # 2
    # @action(
    #     detail=False,
    #     methods=["GET"],
    #     url_path="user-orders",
    #     # permission_classes=[IsAuthenticated],
    # )
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)


# class OrderListAPIView(generics.ListCreateAPIView):
#     queryset = Order.objects.prefetch_related("items__product")
#     serializer_class = OrderSerializer


class UserOrderListAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # Get Orders for the logged in user
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer(
            {
                "products": products,
                "count": len(products),
                "max_price": products.aggregate(max_price=Max("price"))["max_price"],
            }
        )
        return Response(serializer.data)


# @api_view(["GET"])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer(
#         {
#             "products": products,
#             "count": len(products),
#             "max_price": products.aggregate(max_price=Max("price"))["max_price"],
#         }
#     )
#     return Response(serializer.data)


# @api_view(["GET"])
# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)

# @api_view(["GET"])
# def product_detail(request, pk):
#     products = get_object_or_404(Product, pk=pk)
#     serializer = ProductSerializer(products)
#     return Response(serializer.data)

# @api_view(["GET"])
# def order_list(request):
#     # orders = Order.objects.all()
#     orders = Order.objects.prefetch_related("items", "items__product")
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)
