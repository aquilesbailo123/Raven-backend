from django.contrib import admin

from .models import Campaign, FinancialSheet

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('startup', 'status', 'created', 'updated')
    list_filter = ('status', 'created')
    search_fields = ('startup__company_name',)

@admin.register(FinancialSheet)
class FinancialSheetAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'created', 'updated')
    search_fields = ('campaign__startup__company_name',)
