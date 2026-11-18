from django.contrib import admin
from .models import SiteSettings, SystemSettings, ServerSettings, AuditLog, Reports


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "site_name",
        "site_title",
        "is_active",
        "maintenance_mode",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "maintenance_mode",
    )

    readonly_fields = (
        "updated_at",
    )

    fieldsets = (
        ("اطلاعات وب‌سایت", {
            "fields": (
                "site_name",
                "site_title",
                "site_description",
            )
        }),

        ("تصاویر وب‌سایت", {
            "fields": (
                "logo",
                "favicon",
            )
        }),

        ("وضعیت وب‌سایت", {
            "fields": (
                "is_active",
                "maintenance_mode",
                "maintenance_message",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "updated_at",
            )
        }),
    )


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "default_language",
        "timezone",
        "items_per_page",
        "max_upload_size_mb",
        "allow_registration",
        "notifications_enabled",
        "updated_at",
    )

    list_filter = (
        "default_language",
        "allow_registration",
        "notifications_enabled",
    )

    readonly_fields = (
        "updated_at",
    )

    fieldsets = (
        ("تنظیمات زبان و زمان", {
            "fields": (
                "default_language",
                "timezone",
            )
        }),

        ("تنظیمات نمایش و آپلود", {
            "fields": (
                "items_per_page",
                "max_upload_size_mb",
            )
        }),

        ("تنظیمات دسترسی و اعلان‌ها", {
            "fields": (
                "allow_registration",
                "notifications_enabled",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "updated_at",
            )
        }),
    )

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ServerSettings)
class ServerSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "environment",
        "is_active",
        "last_checked",
        "updated_at",
    )

    list_filter = (
        "environment",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("اطلاعات سرور", {
            "fields": (
                "name",
                "environment",
                "description",
            )
        }),

        ("وضعیت سرور", {
            "fields": (
                "is_active",
                "last_checked",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "created_at",
    )

    list_filter = (
        "action",
        "app_label",
        "created_at",
    )

    search_fields = (
        "user__username",
        "object_repr",
        "description",
        "object_id",
    )

    readonly_fields = (
        "user",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "description",
        "changes",
        "created_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Reports)
class ReportsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.method == "GET"

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    list_display = (
        "user",
        "action",
        "app_label",
        "model_name",
        "object_repr",
        "created_at",
    )

    list_filter = (
        "action",
        "app_label",
        "created_at",
    )

    search_fields = (
        "user__username",
        "object_repr",
        "description",
        "object_id",
    )

    readonly_fields = (
        "user",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "description",
        "changes",
        "created_at",
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"
