import django_filters
from django import forms

from .models import (
    CashFlowRecord,
    Status,
    OperationType,
    Category,
    Subcategory,
)


class CashFlowRecordFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='Дата от',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )

    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='Дата до',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )

    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label='Статус',
        empty_label='Все статусы',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    operation_type = django_filters.ModelChoiceFilter(
        queryset=OperationType.objects.all(),
        label='Тип',
        empty_label='Все типы',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.select_related('operation_type').all(),
        label='Категория',
        empty_label='Все категории',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    subcategory = django_filters.ModelChoiceFilter(
        queryset=Subcategory.objects.select_related('category').all(),
        label='Подкатегория',
        empty_label='Все подкатегории',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    class Meta:
        model = CashFlowRecord
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        operation_type_id = None
        category_id = None

        if self.is_bound:
            operation_type_id = self.data.get('operation_type')
            category_id = self.data.get('category')

        self.filters['category'].queryset = (
            Category.objects
            .select_related('operation_type')
            .order_by('name')
        )

        self.filters['subcategory'].queryset = (
            Subcategory.objects
            .select_related('category')
            .order_by('name')
        )

        if operation_type_id:
            self.filters['category'].queryset = (
                Category.objects
                .filter(operation_type_id=operation_type_id)
                .select_related('operation_type')
                .order_by('name')
            )

            self.filters['subcategory'].queryset = (
                Subcategory.objects
                .filter(category__operation_type_id=operation_type_id)
                .select_related('category')
                .order_by('name')
            )

        if category_id:
            self.filters['subcategory'].queryset = (
                Subcategory.objects
                .filter(category_id=category_id)
                .select_related('category')
                .order_by('name')
            )