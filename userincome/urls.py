from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='income'),
    path('add-income', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.income_edit, name='income-edit'),
    path('income-delete/<int:id>', views.delete_income, name='income-delete'),
    path('search-income', csrf_exempt(views.search_income), name='search_income'),
    path('income_source_summary', views.income_source_summary, name='income_source_summary'),
    path('stats-income', views.stats_view_income, name='stats-income'),
    path('export_csv', views.export_csv, name='export-csv'),
    path('export_excel', views.export_excel, name='export-excel'),
    path('lista-fuentes/', views.lista_source, name='lista_source'),
    path('add-source/', views.add_source, name='add_source'),
    path('source-delete/<int:id>', views.delete_source, name='delete_source'),
    path('search-source', csrf_exempt(views.search_source), name='search_source'),


]