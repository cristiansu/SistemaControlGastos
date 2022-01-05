from django.core.checks import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import encoding
from .models import Category, Expense
from userpreferences.models import UserPreference
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse, request
#para exportacion csv y excel
import datetime
import csv
import xlwt
#para exportación pdf
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
#para CRUD category
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)
from django.urls import reverse_lazy

# Create your views here.

@login_required(login_url='/authentication/login')
def inicio(request):

    return render(request, 'expenses/inicio.html')

def search_expenses(request):
    if request.method=='POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)

        data = expenses.values()

        return JsonResponse(list(data), safe=False)

    

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.filter(usuarioC=request.user)
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses':expenses,
        'page_obj':page_obj,
        'currency':currency
    }
    return render(request, 'expenses/index.html', context=context)

@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.filter(usuarioC=request.user)
    context = {
        'categories':categories,
        'values':request.POST
        }
    if request.method=='GET':
 
        return render(request, 'expenses/add_expenses.html', context)

    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Monto no ingresado')
            return render(request, 'expenses/add_expenses.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'Description no ingresada')
            return render(request, 'expenses/add_expenses.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        messages.success(request, 'Gasto registrado correctamente')

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.filter(usuarioC=request.user)
    context = {
        'expense':expense,
        'values':expense,
        'categories':categories
    }
    if request.method=='GET':
        
        return render(request, 'expenses/edit-expense.html', context)
    if request.method=='POST':

        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Monto no ingresado')
            return render(request, 'expenses/edit-expense.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'Description no ingresada')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.description=description

        expense.save()
        messages.success(request, 'Gasto editado correctamente')

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Gasto eliminado')

    return redirect('expenses')

#------funciones para gráfico--------------------

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)

    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses))) #se usa set para no considerar duplicados

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount

        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')

#------funciones para exportar datos CSV/Excel/PDF--------------------

def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Gastos'+str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Monto','Descripcion','Categoria','Fecha'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Gastos'+str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Gastos')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True

    columns = ['Monto','Descripcion','Categoria','Fecha']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount','description','category','date')

    for row in rows:
        row_num +=1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response

'''   
NO FUNCIONA - error:
*********  [Errno 13] Permission denied: 'C:\\Users\\saave\\AppData\\Local\\Temp\\tmp88r4_ar3'  ************

def export_pdf(request):
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Gastos'+str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)

    html_string = render_to_string('expenses/pdf-output.html', {'expenses':[], 'total':0}) #es el template html
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output = open(output.name, 'rb')
        response.write(output.read())

    return response

'''

#------------Search y CRUD Categorias------------------

def search_category(request):
    if request.method=='POST':
        search_str = json.loads(request.body).get('searchText')

        categoria = Category.objects.filter(name__icontains=search_str, usuarioC=request.user)

        data = categoria.values()

        return JsonResponse(list(data), safe=False)

def lista_category(request):
    expenses = Expense.objects.filter(owner=request.user)
    categorias = Category.objects.filter(usuarioC=request.user)
    
    paginator = Paginator(categorias, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context={
        'categorias':categorias, 
        'page_obj':page_obj,
    }

    return render(request, 'expenses/lista-categorias.html', context=context)

@login_required(login_url='/authentication/login')
def add_category(request):
    categories = Category.objects.filter(usuarioC=request.user)
    context = {
        'categories':categories,
        'values':request.POST
        }
    if request.method=='GET':
 
        return render(request, 'expenses/add-category.html', context)

    if request.method=='POST':
        category = request.POST['category']

        if not category:
            messages.error(request, 'Categoría no ingresada')
            return render(request, 'expenses/add-category.html', context)

        Category.objects.create(usuarioC=request.user, name=category)
        messages.success(request, 'Categoria registrado correctamente')

        return redirect('lista_categorias')

#************category_edit****NO SE VA A USAR*****pq no tiene sentido editar categoría. mejor se crea una nueva o se edita
'''
@login_required(login_url='/authentication/login')
def category_edit(request, id):
    categories = Category.objects.get(pk=id)
    context = {
        'categories':categories,
        'values':request.POST
        }
    if request.method=='GET':
 
        return render(request, 'expenses/edit-category.html', context)

    if request.method=='POST':
        category = request.POST['category']

        if not category:
            messages.error(request, 'Categoría no ingresada')
            return render(request, 'expenses/edit-category.html', context)

        categories.usuarioC = request.user
        categories.name = category

        categories.save()
        messages.success(request, 'Categoría editada correctamente')

        return redirect('lista_categorias')
'''
#************category_edit****NO SE VA A USAR*****pq no tiene sentido editar categoría. mejor se crea una nueva o se edita****FIN COMENTARIO

@login_required(login_url='/authentication/login')
def delete_category(request, id):
    categoria = Category.objects.get(pk=id)
    categoria.delete()
    messages.success(request, 'Categoria eliminada')

    return redirect('lista_categorias')







