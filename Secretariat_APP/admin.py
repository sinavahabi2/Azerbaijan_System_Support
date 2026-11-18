from django.contrib import admin
from django.utils import timezone

from .models import (
    Secretariat,
    SecretariatNumbering,
    SecretariatDocumentType,
    SecretariatCorrespondence,
    CorrespondenceRecipient,
    CorrespondenceAttachment,
    CorrespondenceAction,
    CorrespondenceHistory,
    InternalConversation,
    InternalConversationMember,
    InternalMessage,
    InternalMessageAttachment,
    InternalMessageReadReceipt,
)


# =========================================================
# Base Admin
# =========================================================

class TimestampedAdmin(admin.ModelAdmin):
    """
    تنظیمات مشترک مدل‌های دارای UUID و زمان ایجاد/ویرایش
    """

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    list_per_page = 25
    save_on_top = True


# =========================================================
# Secretariat
# =========================================================

@admin.register(Secretariat)
class SecretariatAdmin(TimestampedAdmin):

    list_display = (
        "title",
        "organization",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    readonly_fields = TimestampedAdmin.readonly_fields

    fieldsets = (
        ("اطلاعات دبیرخانه", {
            "fields": (
                "organization",
                "title",
                "description",
                "is_active",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )


# =========================================================
# Numbering
# =========================================================

@admin.register(SecretariatNumbering)
class SecretariatNumberingAdmin(TimestampedAdmin):

    list_display = (
        "secretariat",
        "branch",
        "year",
        "prefix",
        "next_number",
        "number_digits",
        "is_active",
    )

    list_filter = (
        "year",
        "is_active",
        "secretariat",
    )

    search_fields = (
        "secretariat__title",
        "prefix",
    )

    list_select_related = (
        "secretariat",
        "branch",
    )

    fieldsets = (
        ("محل شماره‌گذاری", {
            "fields": (
                "secretariat",
                "branch",
                "year",
            )
        }),
        ("تنظیمات شماره", {
            "fields": (
                "prefix",
                "next_number",
                "number_digits",
                "is_active",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )


# =========================================================
# Document Types
# =========================================================

@admin.register(SecretariatDocumentType)
class SecretariatDocumentTypeAdmin(TimestampedAdmin):

    list_display = (
        "title",
        "code",
        "secretariat",
        "direction",
        "requires_response",
        "is_active",
    )

    list_filter = (
        "direction",
        "requires_response",
        "is_active",
        "secretariat",
    )

    search_fields = (
        "title",
        "code",
        "description",
        "secretariat__title",
    )

    list_select_related = (
        "secretariat",
    )

    fieldsets = (
        ("مشخصات نوع مکاتبه", {
            "fields": (
                "secretariat",
                "title",
                "code",
                "direction",
                "description",
            )
        }),
        ("تنظیمات", {
            "fields": (
                "requires_response",
                "is_active",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )


# =========================================================
# Correspondence Inlines
# =========================================================

class CorrespondenceRecipientInline(admin.TabularInline):

    model = CorrespondenceRecipient
    extra = 0
    show_change_link = True
    raw_id_fields = (
        "branch",
        "organizational_unit",
        "user",
    )

    fields = (
        "branch",
        "organizational_unit",
        "user",
        "is_copy",
        "is_read",
        "read_at",
    )


class CorrespondenceActionInline(admin.TabularInline):

    model = CorrespondenceAction
    extra = 0
    show_change_link = True

    raw_id_fields = (
        "source_branch",
        "destination_branch",
        "destination_unit",
        "destination_user",
    )

    readonly_fields = (
        "performed_by",
        "created_at",
        "updated_at",
    )

    fields = (
        "action_type",
        "status",
        "source_branch",
        "destination_branch",
        "destination_unit",
        "destination_user",
        "performed_by",
        "description",
        "due_date",
        "completed_at",
        "created_at",
    )


class CorrespondenceAttachmentInline(admin.TabularInline):

    model = CorrespondenceAttachment
    extra = 0
    can_delete = False
    show_change_link = True

    readonly_fields = (
        "file",
        "original_name",
        "description",
        "uploaded_by",
        "id",
        "created_at",
        "updated_at",
    )

    fields = (
        "file",
        "original_name",
        "description",
        "uploaded_by",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        return False


class CorrespondenceHistoryInline(admin.TabularInline):

    model = CorrespondenceHistory
    extra = 0
    can_delete = False
    show_change_link = True

    readonly_fields = (
        "previous_status",
        "new_status",
        "description",
        "changed_by",
        "id",
        "created_at",
        "updated_at",
    )

    fields = (
        "previous_status",
        "new_status",
        "description",
        "changed_by",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        return False


# =========================================================
# Correspondence
# =========================================================

@admin.register(SecretariatCorrespondence)
class SecretariatCorrespondenceAdmin(TimestampedAdmin):

    list_display = (
        "letter_number",
        "subject",
        "secretariat",
        "branch",
        "direction",
        "priority",
        "status",
        "is_confidential",
        "created_at",
    )

    list_filter = (
        "direction",
        "status",
        "priority",
        "is_confidential",
        "year",
        "branch",
        "secretariat",
    )

    search_fields = (
        "letter_number",
        "subject",
        "body",
        "sender_name",
        "sender_organization",
        "recipient_name",
        "recipient_organization",
        "external_letter_number",
    )

    list_select_related = (
        "secretariat",
        "branch",
        "document_type",
        "created_by",
    )

    date_hierarchy = "created_at"

    raw_id_fields = (
        "secretariat",
        "branch",
        "document_type",
        "created_by",
    )

    readonly_fields = TimestampedAdmin.readonly_fields + (
        "created_by",
    )

    inlines = (
        CorrespondenceRecipientInline,
        CorrespondenceActionInline,
        CorrespondenceAttachmentInline,
        CorrespondenceHistoryInline,
    )

    fieldsets = (
        ("مشخصات اصلی نامه", {
            "fields": (
                "secretariat",
                "branch",
                "document_type",
                "direction",
                "subject",
                "body",
            )
        }),
        ("شماره و ثبت نامه", {
            "fields": (
                "year",
                "sequence_number",
                "letter_number",
                "registration_date",
                "registered_at",
                "external_letter_number",
                "external_letter_date",
            )
        }),
        ("اطلاعات فرستنده و گیرنده", {
            "fields": (
                "sender_name",
                "sender_organization",
                "recipient_name",
                "recipient_organization",
            ),
            "classes": ("collapse",),
        }),
        ("وضعیت و پیگیری", {
            "fields": (
                "priority",
                "status",
                "response_deadline",
                "is_confidential",
                "notes",
            )
        }),
        ("اطلاعات ثبت‌کننده", {
            "fields": (
                "created_by",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        ثبت خودکار اقدام‌کننده برای ارجاعات جدید
        """

        instances = formset.save(commit=False)

        for deleted_object in formset.deleted_objects:
            deleted_object.delete()

        for instance in instances:
            if (
                isinstance(instance, CorrespondenceAction)
                and not instance.pk
                and not instance.performed_by_id
            ):
                instance.performed_by = request.user

            instance.save()

        formset.save_m2m()

    def has_delete_permission(self, request, obj=None):
        # حذف مستقیم پرونده‌های مکاتبات از پنل غیرفعال است.
        return False


# =========================================================
# Correspondence Recipients
# =========================================================

@admin.register(CorrespondenceRecipient)
class CorrespondenceRecipientAdmin(TimestampedAdmin):

    list_display = (
        "correspondence",
        "branch",
        "organizational_unit",
        "user",
        "is_copy",
        "is_read",
        "read_at",
    )

    list_filter = (
        "is_copy",
        "is_read",
        "branch",
    )

    search_fields = (
        "correspondence__letter_number",
        "correspondence__subject",
        "user__username",
    )

    list_select_related = (
        "correspondence",
        "branch",
        "organizational_unit",
        "user",
    )

    raw_id_fields = (
        "correspondence",
        "branch",
        "organizational_unit",
        "user",
    )


# =========================================================
# Correspondence Attachments
# =========================================================

@admin.register(CorrespondenceAttachment)
class CorrespondenceAttachmentAdmin(TimestampedAdmin):

    list_display = (
        "original_name",
        "correspondence",
        "uploaded_by",
        "created_at",
    )

    search_fields = (
        "original_name",
        "description",
        "correspondence__letter_number",
        "correspondence__subject",
    )

    list_select_related = (
        "correspondence",
        "uploaded_by",
    )

    readonly_fields = (
        "id",
        "correspondence",
        "file",
        "original_name",
        "description",
        "uploaded_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(
            "Secretariat_APP.view_correspondenceattachment"
        )

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Correspondence Actions
# =========================================================

@admin.register(CorrespondenceAction)
class CorrespondenceActionAdmin(TimestampedAdmin):

    list_display = (
        "correspondence",
        "action_type",
        "status",
        "destination_branch",
        "destination_unit",
        "destination_user",
        "performed_by",
        "due_date",
        "completed_at",
    )

    list_filter = (
        "action_type",
        "status",
        "destination_branch",
    )

    search_fields = (
        "correspondence__letter_number",
        "correspondence__subject",
        "description",
        "performed_by__username",
        "destination_user__username",
    )

    list_select_related = (
        "correspondence",
        "source_branch",
        "destination_branch",
        "destination_unit",
        "destination_user",
        "performed_by",
    )

    raw_id_fields = (
        "correspondence",
        "source_branch",
        "destination_branch",
        "destination_unit",
        "destination_user",
        "performed_by",
    )

    readonly_fields = TimestampedAdmin.readonly_fields + (
        "performed_by",
    )

    fieldsets = (
        ("اطلاعات اقدام", {
            "fields": (
                "correspondence",
                "action_type",
                "status",
                "description",
            )
        }),
        ("مبدأ و مقصد", {
            "fields": (
                "source_branch",
                "destination_branch",
                "destination_unit",
                "destination_user",
            )
        }),
        ("زمان‌بندی", {
            "fields": (
                "due_date",
                "completed_at",
            )
        }),
        ("اقدام‌کننده", {
            "fields": (
                "performed_by",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.performed_by_id:
            obj.performed_by = request.user

        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Correspondence History
# =========================================================

@admin.register(CorrespondenceHistory)
class CorrespondenceHistoryAdmin(TimestampedAdmin):

    list_display = (
        "correspondence",
        "previous_status",
        "new_status",
        "changed_by",
        "created_at",
    )

    list_filter = (
        "previous_status",
        "new_status",
    )

    search_fields = (
        "correspondence__letter_number",
        "correspondence__subject",
        "description",
        "changed_by__username",
    )

    list_select_related = (
        "correspondence",
        "changed_by",
    )

    readonly_fields = (
        "id",
        "correspondence",
        "previous_status",
        "new_status",
        "description",
        "changed_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(
            "Secretariat_APP.view_correspondencehistory"
        )

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Internal Conversation Members
# =========================================================

class InternalConversationMemberInline(admin.TabularInline):

    model = InternalConversationMember
    extra = 0
    show_change_link = True

    raw_id_fields = (
        "user",
    )

    readonly_fields = (
        "joined_at",
        "left_at",
        "last_read_at",
        "created_at",
        "updated_at",
    )

    fields = (
        "user",
        "is_admin",
        "is_active",
        "joined_at",
        "left_at",
        "last_read_at",
    )


# =========================================================
# Internal Conversations
# =========================================================

@admin.register(InternalConversation)
class InternalConversationAdmin(TimestampedAdmin):

    list_display = (
        "title",
        "secretariat",
        "conversation_type",
        "status",
        "created_by",
        "last_message_at",
        "created_at",
    )

    list_filter = (
        "conversation_type",
        "status",
        "secretariat",
    )

    search_fields = (
        "title",
        "description",
        "created_by__username",
        "secretariat__title",
    )

    list_select_related = (
        "secretariat",
        "created_by",
    )

    raw_id_fields = (
        "secretariat",
        "created_by",
    )

    readonly_fields = TimestampedAdmin.readonly_fields + (
        "created_by",
        "last_message_at",
    )

    inlines = (
        InternalConversationMemberInline,
    )

    fieldsets = (
        ("مشخصات گفتگو", {
            "fields": (
                "secretariat",
                "conversation_type",
                "title",
                "description",
                "status",
            )
        }),
        ("اطلاعات گفتگو", {
            "fields": (
                "created_by",
                "last_message_at",
            )
        }),
        ("اطلاعات سیستمی", {
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)


# =========================================================
# Internal Conversation Members
# =========================================================

@admin.register(InternalConversationMember)
class InternalConversationMemberAdmin(TimestampedAdmin):

    list_display = (
        "conversation",
        "user",
        "is_admin",
        "is_active",
        "joined_at",
        "left_at",
        "last_read_at",
    )

    list_filter = (
        "is_admin",
        "is_active",
    )

    search_fields = (
        "conversation__title",
        "user__username",
    )

    list_select_related = (
        "conversation",
        "user",
    )

    raw_id_fields = (
        "conversation",
        "user",
    )


# =========================================================
# Internal Messages
# =========================================================

@admin.register(InternalMessage)
class InternalMessageAdmin(TimestampedAdmin):

    list_display = (
        "id",
        "conversation",
        "sender",
        "short_body",
        "is_deleted",
        "created_at",
        "edited_at",
    )

    list_filter = (
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "body",
        "sender__username",
        "conversation__title",
    )

    list_select_related = (
        "conversation",
        "sender",
        "reply_to",
    )

    readonly_fields = (
        "id",
        "conversation",
        "sender",
        "body",
        "reply_to",
        "edited_at",
        "is_deleted",
        "deleted_at",
        "created_at",
        "updated_at",
    )

    @admin.display(description="متن پیام")
    def short_body(self, obj):
        if obj.is_deleted:
            return "پیام حذف‌شده"

        return obj.body[:70]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(
            "Secretariat_APP.view_internalmessage"
        )

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Internal Message Attachments
# =========================================================

@admin.register(InternalMessageAttachment)
class InternalMessageAttachmentAdmin(TimestampedAdmin):

    list_display = (
        "original_name",
        "message",
        "uploaded_by",
        "created_at",
    )

    search_fields = (
        "original_name",
        "message__body",
        "uploaded_by__username",
    )

    list_select_related = (
        "message",
        "uploaded_by",
    )

    readonly_fields = (
        "id",
        "message",
        "file",
        "original_name",
        "uploaded_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(
            "Secretariat_APP.view_internalmessageattachment"
        )

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Internal Message Read Receipts
# =========================================================

@admin.register(InternalMessageReadReceipt)
class InternalMessageReadReceiptAdmin(TimestampedAdmin):

    list_display = (
        "message",
        "user",
        "read_at",
    )

    list_filter = (
        "read_at",
    )

    search_fields = (
        "user__username",
        "message__body",
        "message__conversation__title",
    )

    list_select_related = (
        "message",
        "user",
        "message__conversation",
    )

    readonly_fields = (
        "id",
        "message",
        "user",
        "read_at",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm(
            "Secretariat_APP.view_internalmessagereadreceipt"
        )

    def has_delete_permission(self, request, obj=None):
        return False