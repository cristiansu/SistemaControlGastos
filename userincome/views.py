from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
import datetime
#para importación de archivos
import datetime
import csv
import xlwt
# Create your views here.

def search_income(request):
    if request.method=='POST':
        search_str = json.loads(request.body).get('searchText')

        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)

        data = income.values()

        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.filter(usuarioS=request.user)
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income':income,
        'page_obj':page_obj,
        'currency':currency
    }
    return render(request, 'income/index.html', context=context)

@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.filter(usuarioS=request.user)
    context = {
        'sources':sources,
        'values':request.POST
        }
    if request.method=='GET':
 
        return render(request, 'income/add_income.html', context)

    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Monto no ingresado')
            return render(request, 'income/add_income.html', context)

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'Description no ingresada')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request, 'Ingreso registrado correctamente')

        return redirect('income')

@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.filter(usuarioS=request.user)
    context = {
        'income':income,
        'values':income,
        'sources':sources
    }
    if request.method=='GET':
        
        return render(request, 'income/edit_income.html', context)
    if request.method=='POST':

        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Monto no ingresado')
            return render(request, 'income/edit_income.html', context)

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'Description no ingresada')
            return render(request, 'income/edit_income.html', context)

        #income.owner = request.user
        income.amount=amount
        income.date=date
        income.source=source
        income.description=description

        income.save()
        messages.success(request, 'Ingreso editado correctamente')

        return redirect('income')

@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Ingreso eliminado')

    return redirect('income')


#-----------vistas para gráfico--------------

def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)

    finalrep = {}

    def get_source(income):
        return income.source
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)

        for item in filtered_by_source:
            amount += item.amount

        return amount

    for x in incomes:
        for y in source_list:
            finalrep[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data':finalrep}, safe=False)


def stats_view_income(request):
    return render(request, 'income/stats.html')


#------funciones para exportar datos CSV/Excel/PDF--------------------

def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Ingresos'+str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Monto','Descripcion','Fuente','Fecha'])

    incomes = UserIncome.objects.filter(owner=request.user)

    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Ingresos'+str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Ingresos')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True

    columns = ['Monto','Descripcion','Fuente','Fecha']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = UserIncome.objects.filter(owner=request.user).values_list('amount','description','source','date')

    for row in rows:
        row_num +=1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


#------------Search y CRUD Fuentes------------------

def search_source(request):
    if request.method=='POST':
        search_str = json.loads(request.body).get('searchText')

        fuente = Source.objects.filter(name__icontains=search_str, usuarioS=request.user)

        data = fuente.values()

        return JsonResponse(list(data), safe=False)

def lista_source(request):
    ingresos = UserIncome.objects.filter(owner=request.user)
    fuentes = Source.objects.filter(usuarioS=request.user)
    
    paginator = Paginator(fuentes, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context={
        'fuentes':fuentes, 
        'page_obj':page_obj,
    }

    return render(request, 'income/lista-fuentes.html', context=context)

@login_required(login_url='/authentication/login')
def add_source(request):
    fuentes = Source.objects.filter(usuarioS=request.user)
    context = {
        'fuentes':fuentes,
        'values':request.POST
        }
    if request.method=='GET':
 
        return render(request, 'income/add-source.html', context)

    if request.method=='POST':
        source = request.POST['source']

        if not source:
            messages.error(request, 'Fuente no ingresada')
            return render(request, 'income/add-source.html', context)

        Source.objects.create(usuarioS=request.user, name=source)
        messages.success(request, 'Fuente registrada correctamente')

        return redirect('lista_source')


@login_required(login_url='/authentication/login')
def delete_source(request, id):
    fuente = Source.objects.get(pk=id)
    fuente.delete()
    messages.success(request, 'fuente eliminada')

    return redirect('lista_source')