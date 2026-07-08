from django import forms

from .models import CashFlowRecord, Category, Subcategory


class CashFlowRecordForm(forms.ModelForm):
    date = forms.DateField(
        label='Дата создания',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        )
    )

    class Meta:
        model = CashFlowRecord
        fields = [
            'date',
            'status',
            'operation_type',
            'category',
            'subcategory',
            'amount',
            'comment',
        ]

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'operation_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'subcategory': forms.Select(attrs={
                'class': 'form-select',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Например, 1000',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий к операции',
            }),
        }

        labels = {
            'status': 'Статус',
            'operation_type': 'Тип',
            'category': 'Категория',
            'subcategory': 'Подкатегория',
            'amount': 'Сумма',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].empty_label = 'Выберите статус'
        self.fields['operation_type'].empty_label = 'Выберите тип'
        self.fields['category'].empty_label = 'Выберите категорию'
        self.fields['subcategory'].empty_label = 'Сначала выберите категорию'

        operation_type_id = None
        category_id = None

        if self.is_bound:
            operation_type_id = self.data.get('operation_type')
            category_id = self.data.get('category')
        elif self.instance and self.instance.pk:
            operation_type_id = self.instance.operation_type_id
            category_id = self.instance.category_id

        self.fields['category'].queryset = Category.objects.none()
        self.fields['subcategory'].queryset = Subcategory.objects.none()

        if operation_type_id:
            self.fields['category'].queryset = (
                Category.objects
                .filter(operation_type_id=operation_type_id)
                .select_related('operation_type')
                .order_by('name')
            )

        if category_id:
            self.fields['subcategory'].queryset = (
                Subcategory.objects
                .filter(category_id=category_id)
                .select_related('category')
                .order_by('name')
            )

from .models import Status, OperationType


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Бизнес',
            }),
        }

        labels = {
            'name': 'Название статуса',
        }


class OperationTypeForm(forms.ModelForm):
    class Meta:
        model = OperationType
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Списание',
            }),
        }

        labels = {
            'name': 'Название типа',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'operation_type']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Маркетинг',
            }),
            'operation_type': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

        labels = {
            'name': 'Название категории',
            'operation_type': 'Тип операции',
        }


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'category']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Avito',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

        labels = {
            'name': 'Название подкатегории',
            'category': 'Категория',
        }