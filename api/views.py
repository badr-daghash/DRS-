from django.db.models import Max, Q, F, Sum
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

# from rest_framework.views import APIView
from rest_framework.decorators import action
from api.filters import InStockFilterBackend, ProductFilter, OrderFilter
from api.models import Order, OrderItem, Product
from api.serializers import (
    OrderSerializer,
    ProductInfoSerializer,
    ProductSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
)
from rest_framework.exceptions import PermissionDenied

from django.db.models import F, Sum
from adrf.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from asgiref.sync import sync_to_async
from adrf.viewsets import ModelViewSet
from adrf.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter



# @method_decorator(cache_page(60 * 5), name="dispatch")
class ProductAsyncAPIView(ListCreateAPIView):
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "stock"]

    def get_queryset(self):
        return Product.objects.only("id", "name", "price", "stock", "description")

    async def perform_acreate(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can create products.")
        await sync_to_async(serializer.save)()


class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = "product_id"

    async def perform_aupdate(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can update products.")
        await sync_to_async(serializer.save)()

    async def perform_apartial_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can update products.")
        await sync_to_async(serializer.save)()

    async def perform_adestroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can delete products.")
        await sync_to_async(instance.delete)()


class OrderAsyncViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related("items__product")
    permission_classes = [IsAuthenticated]
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items__product")
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)

        for order in qs:
            order.annotated_total = sum(
                item.quantity * item.product.price for item in order.items.all()
        ) 
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer

        elif self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    async def perform_acreate(self, serializer):
        await sync_to_async(serializer.save)(user=self.request.user)

    async def perform_aupdate(self, serializer):
        await sync_to_async(serializer.save)()

    async def perform_apartial_update(self, serializer):
        await sync_to_async(serializer.save)()

    async def perform_adestroy(self, instance):
        await sync_to_async(instance.delete)()

class UserOrderListAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.prefetch_related("items__product").filter(
            user=self.request.user
        )
    
    async def perform_create(self,serializer): 
        await  sync_to_async(serializer.save)(user=self.request.user)
        
        

# class ProductInfoAPIView(APIView):
#     async def get(self, request):
#         products = await sync_to_async(list)(Product.objects.all())
#         max_price = await sync_to_async(
#             lambda: Product.objects.aggregate(max_price=Max("price"))["max_price"]
#         )()
#         serializer = ProductInfoSerializer(
#             {"products": products, "count": len(products), "max_price": max_price}
#         )
#         return Response(serializer.data)


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


# class ProductListAPIView(generics.ListCreateAPIView):
#     # queryset = Product.objects.all()
#     queryset = Product.objects.order_by("pk")  # for paginatiion yield warning
#     serializer_class = ProductSerializer
#     filterset_class = ProductFilter
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#         InStockFilterBackend,
#     ]
#     search_fields = ["name", "description"]
#     ordering_fields = ["name", "price", "stock"]
#     # pagination_class = PageNumberPagination
#     # pagination_class.page_size = 2
#     # pagination_class.page_query_param = 'pagenum'
#     # pagination_class.page_size_query_param = 'size'
#     # pagination_class.max_page_size = 4
#     pagination_class = LimitOffsetPagination

#     # @method_decorator(cache_page(60 * 5 ,key_prefix='product_list'))
#     # def list(self,request , *args, **kwargs):
#     #     return super().list(request,*args,**kwargs)

#     # def get_queryset(self):
#     #     import time
#     #     time.sleep(2)
#     #     return super().get_queryset()

#     def get_permissions(self):
#         self.permission_classes = [AllowAny]
#         if self.request.method == "POST":
#             self.permission_classes = [IsAdminUser]
#         return super().get_permissions()


# class OrderViewSet(viewsets.ModelViewSet):
#     # throttle_scope  = 'orders'
#     queryset = Order.objects.prefetch_related("items__product")
#     # OrderCreateSerializer
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#     filterset_class = OrderFilter
#     filter_backends = [DjangoFilterBackend]

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def get_serializer_class(self):
#         if self.action == "create":
#             return OrderCreateSerializer
#         return super().get_serializer_class()

#     # 1
#     def get_queryset(self):
#         qs = super().get_queryset()
#         if not self.request.user.is_staff:
#             qs = qs.filter(user=self.request.user)

#         return qs

#     # # 2
#     # @action(
#     #     detail=False,
#     #     methods=["GET"],
#     #     url_path="user-orders",
#     #     # permission_classes=[IsAuthenticated],
#     # )
#     # def user_orders(self, request):
#     #     orders = self.get_queryset().filter(user=request.user)
#     #     serializer = self.get_serializer(orders, many=True)
#     #     return Response(serializer.data)


# class ProductCreateAPIView(generics.CreateAPIView):
#     model = Product
#     serializer_class = ProductSerializer


# class OrderListAPIView(generics.ListCreateAPIView):
#     queryset = Order.objects.prefetch_related("items__product")
#     serializer_class = OrderSerializer


# class ProductListAPIView(ListCreateAPIView):
#     serializer_class = ProductSerializer
#     filterset_class = ProductFilter
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#         InStockFilterBackend,
#     ]
#     search_fields = ["name", "description"]
#     ordering_fields = ["name", "price", "stock"]

#     pagination_class = LimitOffsetPagination

#     async def get_queryset(self):
#         return await sync_to_async(
#             lambda: Product.objects.only(
#                 "id", "name", "price", "stock", "description"
#             ).order_by("pk")
#         )()

#     def get_permissions(self):
#         self.permission_classes = [AllowAny]
#         if self.request.method == "POST":
#             self.permission_classes = [IsAdminUser]
#         return super().get_permissions()
