from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Status(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['name']

    def __str__(self):
        return self.name


class OperationType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )

    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Тип операции'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'operation_type'],
                name='unique_category_for_operation_type'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.operation_type})'


class Subcategory(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_subcategory_for_category'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.category.name})'


class CashFlowRecord(models.Model):
    date = models.DateField(
        default=timezone.localdate,
        verbose_name='Дата создания'
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='cashflow_records',
        verbose_name='Статус'
    )

    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.PROTECT,
        related_name='cashflow_records',
        verbose_name='Тип'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='cashflow_records',
        verbose_name='Категория'
    )

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name='cashflow_records',
        verbose_name='Подкатегория'
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Сумма',
        error_messages={
            'max_digits': 'Введите сумму не больше 999 999 999 999.99 ₽',
            'max_decimal_places': 'У суммы должно быть не больше двух знаков после запятой',
            'max_whole_digits': 'Введите сумму не больше 999 999 999 999.99 ₽',
        }
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ['-date', '-id']

    def clean(self):
        errors = {}

        if self.amount is not None and self.amount <= 0:
            errors['amount'] = 'Сумма должна быть больше нуля'

        if self.category_id and self.operation_type_id:
            category_operation_type_id = (
                Category.objects
                .filter(pk=self.category_id)
                .values_list('operation_type_id', flat=True)
                .first()
            )

            if category_operation_type_id != self.operation_type_id:
                errors['category'] = (
                    'Категория не относится к выбранному типу операции'
                )

        if self.subcategory_id and self.category_id:
            subcategory_category_id = (
                Subcategory.objects
                .filter(pk=self.subcategory_id)
                .values_list('category_id', flat=True)
                .first()
            )

            if subcategory_category_id != self.category_id:
                errors['subcategory'] = (
                    'Подкатегория не относится к выбранной категории'
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.date} | {self.operation_type} | {self.amount} ₽'