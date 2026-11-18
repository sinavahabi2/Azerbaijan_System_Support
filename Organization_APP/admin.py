from django.contrib import admin
from Organization_APP.forms import OrganizationMembershipAdminForm
from Organization_APP.services.account_service import create_employee_account
from django.db import transaction

from .models import (
    Organization,
    OrganizationBranch,
    OrganizationalUnit,
    JobPosition,
    OrganizationMembership,
    PositionAssignment,
    ReportingLine,
    OrganizationChart,
    OrganizationChartNode,
)


# =========================================================
# Base Admin
# =========================================================

class BaseOrganizationAdmin(admin.ModelAdmin):
    """
    تنظیمات مشترک پنل مدیریت اپلیکیشن سازمان‌ها
    """

    save_on_top = True
    list_per_page = 25
    show_full_result_count = True

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# =========================================================
# Organization Branch Inline
# =========================================================

class OrganizationBranchInline(admin.TabularInline):
    model = OrganizationBranch

    extra = 0
    show_change_link = True

    autocomplete_fields = (
        "manager",
    )

    fields = (
        "code",
        "name",
        "manager",
        "phone",
        "email",
        "is_headquarters",
        "is_active",
    )


# =========================================================
# Organization Admin
# =========================================================

@admin.register(Organization)
class OrganizationAdmin(BaseOrganizationAdmin):
    list_display = (
        "name",
        "code",
        "legal_name",
        "email",
        "phone",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "legal_name",
        "email",
        "phone",
    )

    ordering = (
        "name",
    )

    list_editable = (
        "is_active",
    )

    inlines = (
        OrganizationBranchInline,
    )

    fieldsets = (
        ("اطلاعات اصلی سازمان", {
            "fields": (
                "code",
                "name",
                "legal_name",
                "description",
            )
        }),

        ("اطلاعات ارتباطی", {
            "fields": (
                "email",
                "phone",
                "website",
            )
        }),

        ("وضعیت سازمان", {
            "fields": (
                "is_active",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Organization Branch Admin
# =========================================================

@admin.register(OrganizationBranch)
class OrganizationBranchAdmin(BaseOrganizationAdmin):
    list_display = (
        "name",
        "code",
        "organization",
        "manager",
        "is_headquarters",
        "is_active",
    )

    list_display_links = (
        "name",
        "code",
    )

    list_filter = (
        "organization",
        "is_headquarters",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "organization__name",
        "manager__employee_code",
        "manager__user__username",
        "manager__user__first_name",
        "manager__user__last_name",
        "phone",
        "email",
    )

    autocomplete_fields = (
        "organization",
        "manager",
    )

    ordering = (
        "organization",
        "name",
    )

    fieldsets = (
        ("اطلاعات شعبه", {
            "fields": (
                "organization",
                "code",
                "name",
                "description",
            )
        }),

        ("مسئولیت و ارتباطات", {
            "fields": (
                "manager",
                "phone",
                "email",
                "address",
            )
        }),

        ("تنظیمات شعبه", {
            "fields": (
                "is_headquarters",
                "is_active",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Organizational Unit Admin
# =========================================================

@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(BaseOrganizationAdmin):
    list_display = (
        "name",
        "code",
        "organization",
        "branch",
        "parent",
        "unit_type",
        "manager",
        "is_active",
    )

    list_display_links = (
        "name",
        "code",
    )

    list_filter = (
        "organization",
        "branch",
        "unit_type",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "organization__name",
        "branch__name",
        "parent__name",
        "manager__employee_code",
        "manager__user__username",
        "manager__user__first_name",
        "manager__user__last_name",
    )

    autocomplete_fields = (
        "organization",
        "branch",
        "parent",
        "manager",
    )

    ordering = (
        "organization",
        "name",
    )

    fieldsets = (
        ("اطلاعات اصلی واحد", {
            "fields": (
                "organization",
                "branch",
                "parent",
                "code",
                "name",
                "unit_type",
            )
        }),

        ("مسئولیت و توضیحات", {
            "fields": (
                "manager",
                "description",
            )
        }),

        ("وضعیت", {
            "fields": (
                "is_active",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Job Position Admin
# =========================================================

@admin.register(JobPosition)
class JobPositionAdmin(BaseOrganizationAdmin):
    list_display = (
        "title",
        "code",
        "organization",
        "level",
        "is_managerial",
        "is_active",
    )

    list_display_links = (
        "title",
        "code",
    )

    list_filter = (
        "organization",
        "level",
        "is_managerial",
        "is_active",
    )

    search_fields = (
        "title",
        "code",
        "organization__name",
        "description",
    )

    autocomplete_fields = (
        "organization",
    )

    ordering = (
        "organization",
        "level",
        "title",
    )

    fieldsets = (
        ("اطلاعات سمت", {
            "fields": (
                "organization",
                "code",
                "title",
                "level",
            )
        }),

        ("شرح وظایف", {
            "fields": (
                "description",
            )
        }),

        ("تنظیمات سمت", {
            "fields": (
                "is_managerial",
                "is_active",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Organization Membership Admin
# =========================================================

@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(BaseOrganizationAdmin):
    form = OrganizationMembershipAdminForm

    list_display = (
        "employee_code",
        "get_full_name",
        "organization",
        "employment_type",
        "status",
        "start_date",
        "end_date",
    )

    list_display_links = ("employee_code", "get_full_name")

    list_filter = (
        "organization",
        "employment_type",
        "status",
        "start_date",
    )

    search_fields = (
        "employee_code",
        "organization__name",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    autocomplete_fields = ("organization",)

    ordering = ("organization", "employee_code")

    date_hierarchy = "start_date"

    fieldsets = (
        ("اطلاعات سازمانی", {
            "fields": (
                "organization",
                "employee_code",
                "first_name",
                "last_name",
                "email",
            )
        }),
        ("اطلاعات همکاری", {
            "fields": (
                "employment_type",
                "status",
                "start_date",
                "end_date",
            )
        }),
        ("توضیحات", {
            "fields": ("notes",)
        }),
        ("اطلاعات سیستمی", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="نام و نام خانوادگی", ordering="user__first_name")
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.get_username()

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if change:
            obj.user.first_name = form.cleaned_data["first_name"]
            obj.user.last_name = form.cleaned_data["last_name"]
            obj.user.email = form.cleaned_data["email"]

            obj.user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )

            super().save_model(request, obj, form, change)
            return

        user = create_employee_account(
            organization=obj.organization,
            employee_code=obj.employee_code,
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        )

        obj.user = user
        obj.must_change_password = True

        super().save_model(request, obj, form, change)


# =========================================================
# Position Assignment Admin
# =========================================================

@admin.register(PositionAssignment)
class PositionAssignmentAdmin(BaseOrganizationAdmin):
    list_display = (
        "membership",
        "position",
        "organizational_unit",
        "branch",
        "is_primary",
        "is_active",
        "start_date",
        "end_date",
    )

    list_filter = (
        "is_primary",
        "is_active",
        "position__organization",
        "position__level",
        "branch",
        "start_date",
    )

    search_fields = (
        "membership__employee_code",
        "membership__user__username",
        "membership__user__first_name",
        "membership__user__last_name",
        "position__title",
        "position__code",
        "organizational_unit__name",
        "branch__name",
    )

    autocomplete_fields = (
        "membership",
        "position",
        "organizational_unit",
        "branch",
    )

    ordering = (
        "membership",
        "-is_primary",
        "position",
    )

    date_hierarchy = "start_date"

    fieldsets = (
        ("اطلاعات انتساب", {
            "fields": (
                "membership",
                "position",
                "organizational_unit",
                "branch",
            )
        }),

        ("وضعیت مسئولیت", {
            "fields": (
                "is_primary",
                "is_active",
                "start_date",
                "end_date",
            )
        }),

        ("توضیحات", {
            "fields": (
                "description",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Reporting Line Admin
# =========================================================

@admin.register(ReportingLine)
class ReportingLineAdmin(BaseOrganizationAdmin):
    list_display = (
        "subordinate",
        "manager",
        "relationship_type",
        "is_active",
        "start_date",
        "end_date",
    )

    list_filter = (
        "relationship_type",
        "is_active",
        "start_date",
    )

    search_fields = (
        "subordinate__employee_code",
        "subordinate__user__username",
        "subordinate__user__first_name",
        "subordinate__user__last_name",
        "manager__employee_code",
        "manager__user__username",
        "manager__user__first_name",
        "manager__user__last_name",
    )

    autocomplete_fields = (
        "subordinate",
        "manager",
    )

    ordering = (
        "subordinate",
        "relationship_type",
    )

    date_hierarchy = "start_date"

    fieldsets = (
        ("اطلاعات سلسله‌مراتب", {
            "fields": (
                "subordinate",
                "manager",
                "relationship_type",
            )
        }),

        ("وضعیت ارتباط", {
            "fields": (
                "is_active",
                "start_date",
                "end_date",
            )
        }),

        ("توضیحات", {
            "fields": (
                "description",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Organization Chart Node Inline
# =========================================================

class OrganizationChartNodeInline(admin.TabularInline):
    model = OrganizationChartNode

    extra = 0
    show_change_link = True

    autocomplete_fields = (
        "parent",
        "organizational_unit",
        "position",
        "membership",
    )

    fields = (
        "parent",
        "node_type",
        "organizational_unit",
        "position",
        "membership",
        "title",
        "sort_order",
    )


# =========================================================
# Organization Chart Admin
# =========================================================

@admin.register(OrganizationChart)
class OrganizationChartAdmin(BaseOrganizationAdmin):
    list_display = (
        "title",
        "organization",
        "version",
        "status",
        "effective_from",
        "effective_until",
        "is_current",
        "published_at",
    )

    list_display_links = (
        "title",
    )

    list_filter = (
        "organization",
        "status",
        "is_current",
        "effective_from",
    )

    search_fields = (
        "title",
        "description",
        "organization__name",
    )

    autocomplete_fields = (
        "organization",
    )

    ordering = (
        "organization",
        "-version",
    )

    date_hierarchy = "effective_from"

    inlines = (
        OrganizationChartNodeInline,
    )

    fieldsets = (
        ("اطلاعات چارت", {
            "fields": (
                "organization",
                "version",
                "title",
                "description",
            )
        }),

        ("وضعیت انتشار", {
            "fields": (
                "status",
                "is_current",
                "published_at",
            )
        }),

        ("بازه اعتبار", {
            "fields": (
                "effective_from",
                "effective_until",
            )
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )


# =========================================================
# Organization Chart Node Admin
# =========================================================

@admin.register(OrganizationChartNode)
class OrganizationChartNodeAdmin(BaseOrganizationAdmin):
    list_display = (
        "title",
        "chart",
        "node_type",
        "parent",
        "organizational_unit",
        "position",
        "membership",
        "sort_order",
    )

    list_display_links = (
        "title",
    )

    list_filter = (
        "chart__organization",
        "chart",
        "node_type",
    )

    search_fields = (
        "title",
        "chart__title",
        "organizational_unit__name",
        "position__title",
        "membership__employee_code",
        "membership__user__username",
        "membership__user__first_name",
        "membership__user__last_name",
    )

    autocomplete_fields = (
        "chart",
        "parent",
        "organizational_unit",
        "position",
        "membership",
    )

    ordering = (
        "chart",
        "sort_order",
        "created_at",
    )

    fieldsets = (
        ("اطلاعات گره", {
            "fields": (
                "chart",
                "parent",
                "node_type",
                "title",
                "sort_order",
            )
        }),

        ("عنصر سازمانی", {
            "fields": (
                "organizational_unit",
                "position",
                "membership",
            )
        }),

        ("اطلاعات تکمیلی", {
            "fields": (
                "metadata",
            ),
            "classes": (
                "collapse",
            ),
        }),

        ("اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )
