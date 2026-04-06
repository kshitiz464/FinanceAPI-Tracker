from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Transaction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with role management."""
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['role', 'is_active']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {
            'fields': ('role',),
            'description': 'Assign user role for API access control.',
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {
            'fields': ('role', 'email'),
        }),
    )

    actions = ['make_viewer', 'make_analyst', 'make_admin', 'deactivate_users']

    @admin.action(description='Set role to Viewer')
    def make_viewer(self, request, queryset):
        queryset.update(role='viewer')

    @admin.action(description='Set role to Analyst')
    def make_analyst(self, request, queryset):
        queryset.update(role='analyst')

    @admin.action(description='Set role to Admin')
    def make_admin(self, request, queryset):
        queryset.update(role='admin')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Enhanced Transaction admin with filtering, search, and actions."""
    list_display = [
        'id', 'amount_display', 'type', 'category', 'date',
        'created_by', 'is_deleted', 'created_at',
    ]
    list_filter = ['type', 'is_deleted', 'date', 'created_at']
    search_fields = ['category', 'description', 'created_by__username']
    # Removed list_editable — it causes the blank '---' action dropdown bug
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('amount', 'type', 'category', 'date', 'description'),
        }),
        ('Ownership', {
            'fields': ('created_by',),
        }),
        ('Status', {
            'fields': ('is_deleted',),
            'description': 'Soft-deleted records are hidden from the API.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['soft_delete', 'restore']

    @admin.action(description='Soft delete selected transactions')
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    @admin.action(description='Restore soft-deleted transactions')
    def restore(self, request, queryset):
        queryset.update(is_deleted=False)

    @admin.display(description='Amount', ordering='amount')
    def amount_display(self, obj):
        """Display amount with color-coded currency formatting."""
        from django.utils.html import format_html
        color = '#2ecc71' if obj.type == 'income' else '#e74c3c'
        sign = '+' if obj.type == 'income' else '-'
        formatted = "{:,.2f}".format(obj.amount)
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}&#8377;{}</span>',
            color, sign, formatted,
        )

    def save_model(self, request, obj, form, change):
        """Auto-assign created_by on new transaction."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
