from django.contrib import admin
from .models import UserIncome, Source

# Register your models here.

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'description', 'owner', 'source',)
    search_fields = ('description', 'source', 'date',)
    list_per_page = 10

admin.site.register(UserIncome, IncomeAdmin)
admin.site.register(Source)
