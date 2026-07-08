from django.core.exceptions import ValidationError
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
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма'
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
        if self.category and self.operation_type:
            if self.category.operation_type_id != self.operation_type_id:
                raise ValidationError({
                    'category': 'Категория не относится к выбранному типу.'
                })

        if self.subcategory and self.category:
            if self.subcategory.category_id != self.category_id:
                raise ValidationError({
                    'subcategory': 'Подкатегория не относится к выбранной категории.'
                })

        if self.amount is not None and self.amount <= 0:
            raise ValidationError({
                'amount': 'Сумма должна быть больше нуля.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.date} | {self.operation_type} | {self.amount} ₽'