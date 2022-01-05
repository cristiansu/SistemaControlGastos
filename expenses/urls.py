from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='expenses'),
    path('inicio', views.inicio, name='init'),
    path('add-expenses', views.add_expense, name='add-expenses'),
    path('edit-expenses/<int:id>', views.expense_edit, name='expense-edit'),
    path('expense-delete/<int:id>', views.delete_expense, name='expense-delete'),
    path('search-expenses', csrf_exempt(views.search_expenses), name='search_expenses'),
    path('expense_category_summary', views.expense_category_summary, name='expense_category_summary'),
    path('stats', views.stats_view, name='stats'),
    path('export_csv', views.export_csv, name='export-csv'),
    path('export_excel', views.export_excel, name='export-excel'),
    #path('export_pdf', views.export_pdf, name='export-pdf'),
    path('lista-categorias/', views.lista_category, name='lista_categorias'),
    path('add-category/', views.add_category, name='add_category'),
    #path('edit-category/<int:id>', views.category_edit, name='category_edit'),
    path('category-delete/<int:id>', views.delete_category, name='delete_category'),
    path('search-category', csrf_exempt(views.search_category), name='search_category'),


]
