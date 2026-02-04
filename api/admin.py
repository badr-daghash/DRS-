from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline

from unfold.contrib.filters.admin import (RangeDateFilter, SliderNumericFilter,
                                          TextFilter)
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from api.models import Order, OrderItem, Product, User


class AccountEmailFilter(TextFilter):
    title = "email"
    parameter_name = "email"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(email__icontains=self.value())
        return queryset


class AccountUsernameFilter(TextFilter):
    title = "username"
    parameter_name = "username"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(username__icontains=self.value())
        return queryset


class AccountAdmin(UserAdmin, ModelAdmin):
    list_display = (
        "email",
        "username",
        "date_joined",
        "last_login",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "username")
    readonly_fields = ("date_joined", "last_login")
    list_filter_submit = True
    list_filter = (
        AccountEmailFilter,
        AccountUsernameFilter,
        ("date_joined", RangeDateFilter),
        "is_staff",
        "is_active",
    )


class OrderItemInline(TabularInline):
    model = OrderItem


class OrderAdmin(ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("order_id", "status", "user", "created_at")
    list_filter_submit = True
    list_filter = ("status", ("created_at", RangeDateFilter))
    search_fields = ("order_id", "status")


class ProductNameFilter(TextFilter):
    title = "product"
    parameter_name = "product"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name__icontains=self.value()).distinct()
        return queryset


class ProductAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ("id", "name", "description", "price", "stock", "image")
    list_filter_submit = True
    list_filter = (ProductNameFilter, ("price", SliderNumericFilter))
    search_fields = ("name",)
    import_form_class = ImportForm
    export_form_class = ExportForm


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(User, AccountAdmin)
