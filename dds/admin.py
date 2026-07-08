from django.contrib import admin

from .models import (
    Status,
    OperationType,
    Category,
    Subcategory,
    CashFlowRecord,
)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'operation_type')
    list_filter = ('operation_type',)
    search_fields = ('name',)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date',
        'status',
        'operation_type',
        'category',
        'subcategory',
        'amount',
    )
    list_filter = (
        'date',
        'status',
        'operation_type',
        'category',
        'subcategory',
    )
    search_fields = ('comment',)
    date_hierarchy = 'date'