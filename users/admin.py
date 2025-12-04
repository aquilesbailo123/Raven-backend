from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Profile,
    LoginHistory,
    Startup,
    Evidence,
    FinancialInput,
    InvestorPipeline,
    Incubator,
    IncubatorMember,
    Challenge,
    ChallengeApplication,
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'actions_freezed_till', 'is_frozen', 'created', 'updated')
    list_filter = ('actions_freezed_till',)
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created', 'updated')

    def is_frozen(self, obj: Profile):
        if obj.is_actions_frozen():
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_frozen.short_description = 'Actions Frozen'

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip', 'user_agent', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__email', 'user__username', 'ip')
    readonly_fields = ('user', 'ip', 'user_agent', 'timestamp')
    ordering = ('-timestamp',)

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'industry', 'profile', 'TRL_level', 'CRL_level', 'created', 'updated')
    list_filter = ('industry', 'created')
    search_fields = ('company_name', 'profile__user__email')
    readonly_fields = ('created', 'updated')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('profile', 'profile__user')

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('startup', 'type', 'level', 'status', 'description_preview', 'created')
    list_filter = ('status', 'type', 'level', 'created')
    search_fields = ('startup__company_name', 'description')
    readonly_fields = ('created', 'updated')
    ordering = ('-created',)

    fieldsets = (
        ('Basic Information', {'fields': ('startup', 'type', 'level', 'description')}),
        ('File Information', {'fields': ('file_url',)}),
        ('Review', {'fields': ('status', 'reviewer_notes')}),
        ('Timestamps', {'fields': ('created', 'updated'), 'classes': ('collapse',)}),
    )

    def description_preview(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('startup', 'startup__profile')

@admin.register(FinancialInput)
class FinancialInputAdmin(admin.ModelAdmin):
    list_display = ('startup', 'period_date', 'revenue', 'costs', 'cash_balance', 'monthly_burn', 'net_cash_flow_display')
    list_filter = ('period_date', 'created')
    search_fields = ('startup__company_name', 'notes')
    readonly_fields = ('created', 'updated', 'net_cash_flow_display')
    ordering = ('-period_date',)

    fieldsets = (
        ('Basic Information', {'fields': ('startup', 'period_date')}),
        ('Financial Metrics', {'fields': ('revenue', 'costs', 'cash_balance', 'monthly_burn')}),
        ('Calculated', {'fields': ('net_cash_flow_display',)}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created', 'updated'), 'classes': ('collapse',)}),
    )

    def net_cash_flow_display(self, obj):
        net_flow = obj.net_cash_flow
        color = 'green' if net_flow >= 0 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">${:,.2f}</span>', color, net_flow)
    net_cash_flow_display.short_description = 'Net Cash Flow'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('startup', 'startup__profile')

@admin.register(InvestorPipeline)
class InvestorPipelineAdmin(admin.ModelAdmin):
    list_display = ('startup', 'investor_name', 'stage', 'ticket_size_display', 'next_action_date', 'created')
    list_filter = ('stage', 'created', 'next_action_date')
    search_fields = ('startup__company_name', 'investor_name', 'investor_email')
    readonly_fields = ('created', 'updated')
    ordering = ('-created',)

    fieldsets = (
        ('Basic Information', {'fields': ('startup', 'investor_name', 'investor_email')}),
        ('Investment Details', {'fields': ('stage', 'ticket_size')}),
        ('Follow-up', {'fields': ('next_action_date', 'notes')}),
        ('Timestamps', {'fields': ('created', 'updated'), 'classes': ('collapse',)}),
    )

    def ticket_size_display(self, obj):
        if obj.ticket_size:
            return format_html('<span style="font-weight: bold;">${:,.2f}</span>', obj.ticket_size)
        return '-'
    ticket_size_display.short_description = 'Ticket Size'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('startup', 'startup__profile')

@admin.register(Incubator)
class IncubatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'created', 'updated')
    list_filter = ('created',)
    search_fields = ('name', 'profile__user__email')
    readonly_fields = ('created', 'updated')

@admin.register(IncubatorMember)
class IncubatorMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'role', 'incubator', 'created', 'updated')
    list_filter = ('role', 'incubator')
    search_fields = ('full_name', 'email', 'incubator__name')
    readonly_fields = ('created', 'updated')

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'incubator', 'status', 'budget', 'deadline', 'created', 'updated')
    list_filter = ('status', 'incubator')
    search_fields = ('title', 'incubator__name')
    readonly_fields = ('created', 'updated')

@admin.register(ChallengeApplication)
class ChallengeApplicationAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'startup', 'created', 'updated')
    list_filter = ('challenge__status', 'challenge__incubator')
    search_fields = ('challenge__title', 'startup__company_name')
    readonly_fields = ('created', 'updated')
