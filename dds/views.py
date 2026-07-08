from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models.deletion import ProtectedError

from .filters import CashFlowRecordFilter
from .forms import (
    CashFlowRecordForm,
    StatusForm,
    OperationTypeForm,
    CategoryForm,
    SubcategoryForm,
)
from .models import (
    CashFlowRecord,
    Status,
    OperationType,
    Category,
    Subcategory,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.utils import timezone


def record_list(request):
    records = (
        CashFlowRecord.objects
        .select_related(
            'status',
            'operation_type',
            'category',
            'subcategory',
        )
        .all()
    )

    record_filter = CashFlowRecordFilter(
        request.GET,
        queryset=records,
    )

    filtered_records = record_filter.qs

    total_income = (
        filtered_records
        .filter(operation_type__name__iexact='Пополнение')
        .aggregate(total=Sum('amount'))
        .get('total') or 0
    )

    total_expense = (
        filtered_records
        .filter(operation_type__name__iexact='Списание')
        .aggregate(total=Sum('amount'))
        .get('total') or 0
    )

    balance = total_income - total_expense

    context = {
        'filter': record_filter,
        'records': filtered_records,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }

    return render(request, 'dds/record_list.html', context)


def record_create(request):
    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Запись ДДС успешно создана.')
            return redirect('dds:record_list')
    else:
        form = CashFlowRecordForm(initial={
            'date': timezone.localdate(),
        })

    context = {
        'form': form,
        'title': 'Добавить запись ДДС',
        'button_text': 'Создать',
    }

    return render(request, 'dds/record_form.html', context)


def record_update(request, pk):
    record = get_object_or_404(CashFlowRecord, pk=pk)

    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST, instance=record)

        if form.is_valid():
            form.save()
            messages.success(request, 'Запись ДДС успешно обновлена.')
            return redirect('dds:record_list')
    else:
        form = CashFlowRecordForm(instance=record)

    context = {
        'form': form,
        'record': record,
        'title': 'Редактировать запись ДДС',
        'button_text': 'Сохранить',
    }

    return render(request, 'dds/record_form.html', context)


def record_delete(request, pk):
    record = get_object_or_404(CashFlowRecord, pk=pk)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Запись ДДС успешно удалена.')
        return redirect('dds:record_list')

    context = {
        'record': record,
    }

    return render(request, 'dds/record_confirm_delete.html', context)

@api_view(['GET'])
def category_list_api(request):
    operation_type_id = request.GET.get('operation_type')

    if not operation_type_id:
        return Response([])

    categories = (
        Category.objects
        .filter(operation_type_id=operation_type_id)
        .select_related('operation_type')
        .order_by('name')
    )

    data = [
        {
            'id': category.id,
            'name': str(category),
        }
        for category in categories
    ]

    return Response(data)


@api_view(['GET'])
def subcategory_list_api(request):
    category_id = request.GET.get('category')

    if not category_id:
        return Response([])

    subcategories = (
        Subcategory.objects
        .filter(category_id=category_id)
        .select_related('category')
        .order_by('name')
    )

    data = [
        {
            'id': subcategory.id,
            'name': str(subcategory),
        }
        for subcategory in subcategories
    ]

    return Response(data)

def reference_list(request):
    context = {
        'statuses': Status.objects.all(),
        'operation_types': OperationType.objects.all(),
        'categories': Category.objects.select_related('operation_type').all(),
        'subcategories': Subcategory.objects.select_related('category').all(),
    }

    return render(request, 'dds/reference_list.html', context)


def reference_create(request, ref_type):
    model_map = {
        'statuses': (StatusForm, 'Статус'),
        'operation-types': (OperationTypeForm, 'Тип операции'),
        'categories': (CategoryForm, 'Категория'),
        'subcategories': (SubcategoryForm, 'Подкатегория'),
    }

    form_class, title = model_map[ref_type]

    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f'{title} успешно создан.')
            return redirect('dds:reference_list')
    else:
        form = form_class()

    context = {
        'form': form,
        'title': f'Добавить: {title}',
        'button_text': 'Создать',
    }

    return render(request, 'dds/reference_form.html', context)


def reference_update(request, ref_type, pk):
    model_map = {
        'statuses': (Status, StatusForm, 'Статус'),
        'operation-types': (OperationType, OperationTypeForm, 'Тип операции'),
        'categories': (Category, CategoryForm, 'Категория'),
        'subcategories': (Subcategory, SubcategoryForm, 'Подкатегория'),
    }

    model_class, form_class, title = model_map[ref_type]
    instance = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            messages.success(request, f'{title} успешно обновлён.')
            return redirect('dds:reference_list')
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
        'title': f'Редактировать: {title}',
        'button_text': 'Сохранить',
    }

    return render(request, 'dds/reference_form.html', context)


def reference_delete(request, ref_type, pk):
    model_map = {
        'statuses': (Status, 'Статус'),
        'operation-types': (OperationType, 'Тип операции'),
        'categories': (Category, 'Категория'),
        'subcategories': (Subcategory, 'Подкатегория'),
    }

    model_class, title = model_map[ref_type]
    instance = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        try:
            instance.delete()
            messages.success(request, f'{title} успешно удалён.')
        except ProtectedError:
            messages.warning(
                request,
                f'{title} нельзя удалить, потому что он используется в записях ДДС.'
            )

        return redirect('dds:reference_list')

    context = {
        'object': instance,
        'title': title,
    }

    return render(request, 'dds/reference_confirm_delete.html', context)