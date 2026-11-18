from django.contrib import admin
from django.db import transaction
from django.utils import timezone

from .models import (
    Ticket,
    TicketAccessCredential,
    TicketAssignment,
    TicketAttachment,
    TicketCategory,
    TicketCustomer,
    TicketDepartment,
    TicketFeedback,
    TicketMessage,
    TicketStatusHistory,
)


# ---------------------------------------------------------------------
# تنظیمات عمومی پنل مدیریت
# ---------------------------------------------------------------------

class TicketBaseAdmin(admin.ModelAdmin):
    """تنظیمات مشترک برای مدل‌های اپلیکیشن تیکت."""

    date_hierarchy = "created_at"
    save_on_top = True


# ---------------------------------------------------------------------
# مشتریان
# ---------------------------------------------------------------------

@admin.register(TicketCustomer)
class TicketCustomerAdmin(TicketBaseAdmin):
    list_display = (
        "full_name",
        "customer_type",
        "company_name",
        "mobile",
        "email",
        "is_active",
        "created_at",
    )
    list_filter = ("customer_type", "is_active", "created_at")
    search_fields = (
        "first_name",
        "last_name",
        "company_name",
        "mobile",
        "email",
    )
    ordering = ("last_name", "first_name")
    list_per_page = 30
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("اطلاعات هویتی", {
            "fields": (
                "customer_type",
                ("first_name", "last_name"),
                "company_name",
            )
        }),
        ("اطلاعات تماس", {
            "fields": ("mobile", "email")
        }),
        ("وضعیت و توضیحات", {
            "fields": ("is_active", "notes")
        }),
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": ("id", "created_at", "updated_at"),
        }),
    )

    @admin.display(description="نام مشتری", ordering="last_name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# ---------------------------------------------------------------------
# واحدهای پشتیبانی
# ---------------------------------------------------------------------

@admin.register(TicketDepartment)
class TicketDepartmentAdmin(TicketBaseAdmin):
    list_display = (
        "name",
        "code",
        "organization",
        "organizational_unit",
        "is_active",
        "sort_order",
    )
    list_filter = ("organization", "is_active")
    search_fields = (
        "name",
        "code",
        "organization__name",
        "organizational_unit__name",
    )
    ordering = ("organization", "sort_order", "name")
    list_editable = ("is_active", "sort_order")
    list_select_related = ("organization", "organizational_unit")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("مشخصات واحد پشتیبانی", {
            "fields": (
                "organization",
                "organizational_unit",
                ("code", "name"),
                "description",
            )
        }),
        ("تنظیمات نمایش", {
            "fields": ("is_active", "sort_order")
        }),
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": ("id", "created_at", "updated_at"),
        }),
    )


# ---------------------------------------------------------------------
# دسته‌بندی تیکت‌ها
# ---------------------------------------------------------------------

@admin.register(TicketCategory)
class TicketCategoryAdmin(TicketBaseAdmin):
    list_display = (
        "title",
        "code",
        "organization",
        "parent",
        "department",
        "is_active",
        "sort_order",
    )
    list_filter = ("organization", "department", "is_active")
    search_fields = (
        "title",
        "code",
        "description",
        "organization__name",
        "department__name",
    )
    ordering = ("organization", "sort_order", "title")
    list_editable = ("is_active", "sort_order")
    list_select_related = ("organization", "parent", "department")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("مشخصات دسته‌بندی", {
            "fields": (
                "organization",
                "parent",
                "department",
                ("code", "title"),
                "description",
            )
        }),
        ("تنظیمات", {
            "fields": ("is_active", "sort_order")
        }),
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": ("id", "created_at", "updated_at"),
        }),
    )


# ---------------------------------------------------------------------
# تیکت‌ها
# ---------------------------------------------------------------------

@admin.register(Ticket)
class TicketAdmin(TicketBaseAdmin):
    list_display = (
        "tracking_code",
        "subject",
        "customer",
        "organization",
        "branch",
        "department",
        "status",
        "priority",
        "last_activity_at",
    )
    list_filter = (
        "organization",
        "branch",
        "department",
        "status",
        "priority",
        "source",
        "customer_visible",
        "created_at",
    )
    search_fields = (
        "tracking_code",
        "subject",
        "initial_message",
        "customer__first_name",
        "customer__last_name",
        "customer__mobile",
        "customer__company_name",
    )
    ordering = ("-last_activity_at", "-created_at")
    list_per_page = 30
    list_select_related = (
        "organization",
        "branch",
        "customer",
        "department",
        "category",
        "created_by_membership",
    )
    readonly_fields = (
        "id",
        "tracking_code",
        "first_response_at",
        "resolved_at",
        "closed_at",
        "last_activity_at",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("شناسه و اطلاعات درخواست", {
            "fields": (
                "tracking_code",
                "organization",
                "branch",
                "customer",
                "subject",
                "initial_message",
                "source",
                "created_by_membership",
            )
        }),
        ("دسته‌بندی و ارجاع جاری", {
            "fields": ("department", "category")
        }),
        ("وضعیت رسیدگی", {
            "fields": (
                ("status", "priority"),
                "customer_visible",
            )
        }),
        ("زمان‌بندی", {
            "fields": (
                "first_response_at",
                "resolved_at",
                "closed_at",
                "last_activity_at",
            )
        }),
        ("اطلاعات سیستمی", {
            "classes": ("collapse",),
            "fields": ("id", "created_at", "updated_at"),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        هنگام تغییر وضعیت از پنل ادمین، رکورد تاریخچه ایجاد می‌کند.
        این کار فقط ثبت تاریخچه است؛ منطق کامل گردش‌کار و ارجاع
        باید در لایه service پروژه پیاده‌سازی شود.
        """
        with transaction.atomic():
            previous_status = None
            if change:
                previous_status = (
                    Ticket.objects.select_for_update()
                    .filter(pk=obj.pk)
                    .values_list("status", flat=True)
                    .first()
                )

            status_changed = change and previous_status != obj.status
            if status_changed:
                obj.last_activity_at = timezone.now()

            super().save_model(request, obj, form, change)

            if not change or status_changed:
                changed_by = None
                if request.user.is_authenticated:
                    changed_by = (
                        obj.organization.memberships
                        .filter(user=request.user)
                        .first()
                    )

                TicketStatusHistory.objects.create(
                    ticket=obj,
                    previous_status=previous_status or "",
                    new_status=obj.status,
                    changed_by_membership=changed_by,
                    description=(
                        "ثبت اولیه تیکت از پنل مدیریت"
                        if not change
                        else "تغییر وضعیت از پنل مدیریت"
                    ),
                )


# ---------------------------------------------------------------------
# اعتبار دسترسی مشتری
# ---------------------------------------------------------------------

@admin.register(TicketAccessCredential)
class TicketAccessCredentialAdmin(TicketBaseAdmin):
    """
    هش رمز محرمانه عمداً در هیچ بخش پنل نمایش داده نمی‌شود.
    این مدل صرفاً برای مشاهده وضعیت امنیتی دسترسی ثبت شده است.
    """

    list_display = (
        "ticket",
        "is_active",
        "failed_attempts",
        "locked_until",
        "is_locked",
        "last_verified_at",
        "secret_changed_at",
    )
    list_filter = ("is_active", "locked_until", "secret_changed_at")
    search_fields = ("ticket__tracking_code", "ticket__subject")
    list_select_related = ("ticket",)
    ordering = ("-updated_at",)
    fields = (
        "ticket",
        "is_active",
        "failed_attempts",
        "locked_until",
        "last_verified_at",
        "secret_changed_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    @admin.display(description="وضعیت قفل", boolean=True)
    def is_locked(self, obj):
        return obj.is_locked

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------
# پیام‌های تیکت
# ---------------------------------------------------------------------

@admin.register(TicketMessage)
class TicketMessageAdmin(TicketBaseAdmin):
    list_display = (
        "ticket",
        "sender_type",
        "sender_display",
        "visibility",
        "is_edited",
        "is_deleted",
        "created_at",
    )
    list_filter = (
        "sender_type",
        "visibility",
        "is_edited",
        "is_deleted",
        "created_at",
    )
    search_fields = (
        "ticket__tracking_code",
        "ticket__subject",
        "body",
        "customer__first_name",
        "customer__last_name",
        "employee_membership__user__username",
    )
    list_select_related = (
        "ticket",
        "customer",
        "employee_membership",
        "employee_membership__user",
    )
    ordering = ("-created_at",)
    fields = (
        "ticket",
        "sender_type",
        "customer",
        "employee_membership",
        "reply_to",
        "body",
        "visibility",
        "is_edited",
        "edited_at",
        "is_deleted",
        "deleted_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    @admin.display(description="فرستنده")
    def sender_display(self, obj):
        if obj.customer_id:
            return str(obj.customer)
        if obj.employee_membership_id:
            return str(obj.employee_membership)
        return "سامانه"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------
# پیوست‌ها
# ---------------------------------------------------------------------

@admin.register(TicketAttachment)
class TicketAttachmentAdmin(TicketBaseAdmin):
    list_display = (
        "original_name",
        "ticket",
        "message",
        "uploaded_by_customer",
        "uploaded_by_membership",
        "is_customer_visible",
        "created_at",
    )
    list_filter = (
        "uploaded_by_customer",
        "is_customer_visible",
        "created_at",
    )
    search_fields = (
        "original_name",
        "description",
        "ticket__tracking_code",
        "ticket__subject",
    )
    list_select_related = (
        "ticket",
        "message",
        "uploaded_by_membership",
    )
    ordering = ("-created_at",)
    # فیلد file عمداً در فرم ادمین قرار نگرفته تا لینک عمومی فایل
    # یا دسترسی مستقیم به ذخیره‌سازی خصوصی نمایش داده نشود.
    fields = (
        "ticket",
        "message",
        "original_name",
        "description",
        "uploaded_by_customer",
        "uploaded_by_membership",
        "is_customer_visible",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------
# سوابق ارجاع و انتقال
# ---------------------------------------------------------------------

@admin.register(TicketAssignment)
class TicketAssignmentAdmin(TicketBaseAdmin):
    list_display = (
        "ticket",
        "department",
        "assigned_to",
        "assigned_by",
        "assigned_at",
        "ended_at",
        "is_current",
    )
    list_filter = ("department", "assigned_at", "ended_at")
    search_fields = (
        "ticket__tracking_code",
        "ticket__subject",
        "assigned_to__user__username",
        "assigned_by__user__username",
        "department__name",
    )
    list_select_related = (
        "ticket",
        "department",
        "assigned_to",
        "assigned_by",
    )
    ordering = ("-assigned_at",)
    fields = (
        "ticket",
        "department",
        "assigned_to",
        "assigned_by",
        "note",
        "assigned_at",
        "ended_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    @admin.display(description="ارجاع فعال", boolean=True)
    def is_current(self, obj):
        return obj.ended_at is None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------
# تاریخچه تغییر وضعیت
# ---------------------------------------------------------------------

@admin.register(TicketStatusHistory)
class TicketStatusHistoryAdmin(TicketBaseAdmin):
    list_display = (
        "ticket",
        "previous_status",
        "new_status",
        "changed_by_membership",
        "changed_at",
    )
    list_filter = ("new_status", "changed_at")
    search_fields = (
        "ticket__tracking_code",
        "ticket__subject",
        "description",
        "changed_by_membership__user__username",
    )
    list_select_related = ("ticket", "changed_by_membership")
    ordering = ("-changed_at",)
    fields = (
        "ticket",
        "previous_status",
        "new_status",
        "changed_by_membership",
        "description",
        "changed_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------
# بازخورد مشتری
# ---------------------------------------------------------------------

@admin.register(TicketFeedback)
class TicketFeedbackAdmin(TicketBaseAdmin):
    list_display = (
        "ticket",
        "rating",
        "short_comment",
        "submitted_at",
    )
    list_filter = ("rating", "submitted_at")
    search_fields = (
        "ticket__tracking_code",
        "ticket__subject",
        "comment",
    )
    list_select_related = ("ticket",)
    ordering = ("-submitted_at",)
    fields = (
        "ticket",
        "rating",
        "comment",
        "submitted_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    @admin.display(description="نظر مشتری")
    def short_comment(self, obj):
        if not obj.comment:
            return "—"
        return obj.comment[:70] + ("…" if len(obj.comment) > 70 else "")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
