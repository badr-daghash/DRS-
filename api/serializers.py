from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction
from django.db.models import F, Sum


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "stock",
        )

    def validate_stock(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="product.price"
        )

    class Meta:
        model = OrderItem
        fields = ("product_name", "product_price", "quantity", "item_subtotal")


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity")


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("created_at", "user","status", "items")

    @transaction.atomic  # Ensures atomic DB transaction
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        order_items = [
            OrderItem(order=order, product=item["product"], quantity=item["quantity"])
            for item in items_data
        ]
        OrderItem.objects.bulk_create(order_items)
        return order


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemSerializer(many=True)

    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, source="annotated_total", read_only=True
    )

    class Meta:
        model = Order
        fields = ("order_id", "created_at", "user", "status", "items", "total_price")
        extra_kwargs = {"user": {"read_only": True}}


class OrderListSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, source="annotated_total", read_only=True
    )

    class Meta:
        model = Order
        fields = ("order_id", "created_at", "status", "total_price")


class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
