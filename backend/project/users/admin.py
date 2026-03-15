from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PointTransaction


class UserAdmin(BaseUserAdmin):
    """自定义UserAdmin"""
    list_display = ('username', 'email', 'points', 'level', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'level')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('avatar', 'bio', 'phone', 'points', 'experience', 'level', 'last_checkin', 'checkin_streak')}),
    )


class PointTransactionAdmin(admin.ModelAdmin):
    """积分交易记录Admin"""
    list_display = ('user', 'amount', 'type', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'description')


admin.site.register(User, UserAdmin)
admin.site.register(PointTransaction, PointTransactionAdmin)
