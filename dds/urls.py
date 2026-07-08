from django.urls import path

from . import views

app_name = 'dds'

urlpatterns = [
    path('', views.record_list, name='record_list'),

    path('records/create/', views.record_create, name='record_create'),
    path('records/<int:pk>/edit/', views.record_update, name='record_update'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'),

    path('refs/', views.reference_list, name='reference_list'),
    path('refs/<str:ref_type>/create/', views.reference_create, name='reference_create'),
    path('refs/<str:ref_type>/<int:pk>/edit/', views.reference_update, name='reference_update'),
    path('refs/<str:ref_type>/<int:pk>/delete/', views.reference_delete, name='reference_delete'),

    path('api/categories/', views.category_list_api, name='category_list_api'),
    path('api/subcategories/', views.subcategory_list_api, name='subcategory_list_api'),
]