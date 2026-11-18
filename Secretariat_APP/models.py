
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


# =========================================================
# Base
# =========================================================

class UUIDTimeStampedModel(models.Model):
    """
    مدل پایه:
    شناسه UUID و تاریخ ایجاد و ویرایش
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True


# =========================================================
# Choices
# =========================================================

class DocumentDirection(models.TextChoices):
    INCOMING = "incoming", "وارده"
    OUTGOING = "outgoing", "صادره"
    INTERNAL = "internal", "داخلی"


class DocumentStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    REGISTERED = "registered", "ثبت‌شده"
    IN_PROGRESS = "in_progress", "در حال بررسی"
    REFERRED = "referred", "ارجاع‌شده"
    ANSWERED = "answered", "پاسخ داده‌شده"
    ARCHIVED = "archived", "بایگانی‌شده"
    CANCELLED = "cancelled", "ابطال‌شده"


class DocumentPriority(models.TextChoices):
    NORMAL = "normal", "عادی"
    IMPORTANT = "important", "مهم"
    URGENT = "urgent", "فوری"
    VERY_URGENT = "very_urgent", "خیلی فوری"


class ActionType(models.TextChoices):
    REFER = "refer", "ارجاع"
    REVIEW = "review", "بررسی"
    APPROVE = "approve", "تأیید"
    REJECT = "reject", "رد"
    ANSWER = "answer", "پاسخ"
    FOLLOW_UP = "follow_up", "پیگیری"
    ARCHIVE = "archive", "بایگانی"
    OTHER = "other", "سایر"


class ActionStatus(models.TextChoices):
    PENDING = "pending", "در انتظار"
    ACCEPTED = "accepted", "پذیرفته‌شده"
    COMPLETED = "completed", "انجام‌شده"
    REJECTED = "rejected", "ردشده"
    CANCELLED = "cancelled", "لغوشده"


class ConversationType(models.TextChoices):
    PRIVATE = "private", "خصوصی"
    GROUP = "group", "گروهی"


class ConversationStatus(models.TextChoices):
    ACTIVE = "active", "فعال"
    ARCHIVED = "archived", "بایگانی‌شده"
    CLOSED = "closed", "بسته‌شده"


# =========================================================
# Secretariat
# =========================================================

class Secretariat(UUIDTimeStampedModel):
    """
    دبیرخانه مرکزی هر سازمان.
    هر سازمان فقط یک دبیرخانه دارد.
    شعبه‌ها دبیرخانه جداگانه ندارند.
    """

    organization = models.OneToOneField(
        "Organization_APP.Organization",
        on_delete=models.PROTECT,
        related_name="secretariat",
        verbose_name="سازمان",
    )

    title = models.CharField(
        max_length=200,
        default="دبیرخانه مرکزی",
        verbose_name="عنوان دبیرخانه",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "دبیرخانه"
        verbose_name_plural = "دبیرخانه‌ها"

    def __str__(self):
        return f"{self.title} - {self.organization}"


# =========================================================
# Numbering
# =========================================================

class SecretariatNumbering(UUIDTimeStampedModel):
    """
    تنظیمات شماره‌گذاری نامه‌ها.

    branch=None یعنی ستاد مرکزی.
    هر شعبه شماره‌گذاری مستقل دارد.
    شماره‌گذاری بر اساس سال انجام می‌شود.
    """

    secretariat = models.ForeignKey(
        Secretariat,
        on_delete=models.PROTECT,
        related_name="numbering_settings",
        verbose_name="دبیرخانه",
    )

    branch = models.ForeignKey(
        "Organization_APP.OrganizationBranch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_numbering",
        verbose_name="شعبه",
        help_text="خالی بودن این فیلد به معنی ستاد مرکزی است.",
    )

    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1300)],
        db_index=True,
        verbose_name="سال شماره‌گذاری",
    )

    prefix = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="پیشوند شماره",
    )

    next_number = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="شماره بعدی",
    )

    number_digits = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        verbose_name="تعداد ارقام شماره",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "تنظیم شماره‌گذاری"
        verbose_name_plural = "تنظیمات شماره‌گذاری"
        constraints = [
            models.UniqueConstraint(
                fields=["secretariat", "year"],
                condition=Q(branch__isnull=True),
                name="uniq_secretariat_hq_numbering_year",
            ),
            models.UniqueConstraint(
                fields=["secretariat", "branch", "year"],
                condition=Q(branch__isnull=False),
                name="uniq_secretariat_branch_numbering_year",
            ),
        ]
        indexes = [
            models.Index(
                fields=["secretariat", "year", "is_active"],
            ),
        ]

    def clean(self):
        super().clean()

        if self.branch_id and self.secretariat_id:
            if self.branch.organization_id != self.secretariat.organization_id:
                raise ValidationError({
                    "branch": "این شعبه متعلق به سازمان دبیرخانه نیست."
                })

    def __str__(self):
        branch_name = self.branch or "ستاد مرکزی"
        return f"{self.secretariat} - {branch_name} - {self.year}"


# =========================================================
# Document Types
# =========================================================

class SecretariatDocumentType(UUIDTimeStampedModel):
    """
    انواع مکاتبات قابل استفاده در دبیرخانه.
    """

    secretariat = models.ForeignKey(
        Secretariat,
        on_delete=models.CASCADE,
        related_name="document_types",
        verbose_name="دبیرخانه",
    )

    title = models.CharField(
        max_length=150,
        verbose_name="عنوان نوع مکاتبه",
    )

    code = models.SlugField(
        max_length=50,
        verbose_name="کد نوع مکاتبه",
    )

    direction = models.CharField(
        max_length=20,
        choices=DocumentDirection.choices,
        verbose_name="جهت مکاتبه",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    requires_response = models.BooleanField(
        default=False,
        verbose_name="نیازمند پاسخ",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "نوع مکاتبه"
        verbose_name_plural = "انواع مکاتبات"
        constraints = [
            models.UniqueConstraint(
                fields=["secretariat", "code"],
                name="uniq_secretariat_document_type_code",
            ),
        ]

    def __str__(self):
        return self.title


# =========================================================
# Correspondence
# =========================================================

class SecretariatCorrespondence(UUIDTimeStampedModel):
    """
    پرونده اصلی هر نامه در دبیرخانه.

    شماره نامه در هر سازمان، شعبه و سال یکتا است.
    branch=None یعنی نامه متعلق به ستاد مرکزی است.
    """

    secretariat = models.ForeignKey(
        Secretariat,
        on_delete=models.PROTECT,
        related_name="correspondences",
        verbose_name="دبیرخانه",
    )

    branch = models.ForeignKey(
        "Organization_APP.OrganizationBranch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_correspondences",
        verbose_name="شعبه ثبت‌کننده",
    )

    document_type = models.ForeignKey(
        SecretariatDocumentType,
        on_delete=models.PROTECT,
        related_name="correspondences",
        verbose_name="نوع مکاتبه",
    )

    direction = models.CharField(
        max_length=20,
        choices=DocumentDirection.choices,
        db_index=True,
        verbose_name="جهت نامه",
    )

    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1300)],
        db_index=True,
        verbose_name="سال شماره",
    )

    sequence_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="شماره ترتیبی",
    )

    letter_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="شماره نمایشی نامه",
    )

    subject = models.CharField(
        max_length=300,
        db_index=True,
        verbose_name="موضوع",
    )

    body = models.TextField(
        blank=True,
        verbose_name="متن نامه",
    )

    sender_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="نام فرستنده",
    )

    sender_organization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="سازمان فرستنده",
    )

    recipient_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="نام گیرنده",
    )

    recipient_organization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="سازمان گیرنده",
    )

    external_letter_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شماره نامه خارجی",
    )

    external_letter_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ نامه خارجی",
    )

    registration_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ثبت",
    )

    priority = models.CharField(
        max_length=20,
        choices=DocumentPriority.choices,
        default=DocumentPriority.NORMAL,
        db_index=True,
        verbose_name="اولویت",
    )

    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
        db_index=True,
        verbose_name="وضعیت",
    )

    is_confidential = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="محرمانه",
    )

    response_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name="مهلت پاسخ",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_secretariat_correspondences",
        verbose_name="ثبت‌کننده",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="یادداشت",
    )

    registered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان نهایی ثبت",
    )

    class Meta:
        verbose_name = "مکاتبه"
        verbose_name_plural = "مکاتبات"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "secretariat",
                    "year",
                    "sequence_number",
                ],
                condition=Q(
                    branch__isnull=True,
                    sequence_number__isnull=False,
                ),
                name="uniq_hq_correspondence_number",
            ),
            models.UniqueConstraint(
                fields=[
                    "secretariat",
                    "branch",
                    "year",
                    "sequence_number",
                ],
                condition=Q(
                    branch__isnull=False,
                    sequence_number__isnull=False,
                ),
                name="uniq_branch_correspondence_number",
            ),
        ]
        indexes = [
            models.Index(
                fields=["secretariat", "branch", "status"],
            ),
            models.Index(
                fields=["secretariat", "year", "direction"],
            ),
            models.Index(
                fields=["secretariat", "priority", "status"],
            ),
        ]

    def clean(self):
        super().clean()

        if self.branch_id and self.secretariat_id:
            if self.branch.organization_id != self.secretariat.organization_id:
                raise ValidationError({
                    "branch": "شعبه انتخاب‌شده متعلق به این سازمان نیست."
                })

        if self.document_type_id and self.secretariat_id:
            if self.document_type.secretariat_id != self.secretariat_id:
                raise ValidationError({
                    "document_type": "نوع مکاتبه متعلق به دبیرخانه دیگری است."
                })

        if self.direction and self.document_type_id:
            if self.direction != self.document_type.direction:
                raise ValidationError({
                    "direction": "جهت نامه با نوع مکاتبه مطابقت ندارد."
                })

    def __str__(self):
        return f"{self.letter_number or 'بدون شماره'} - {self.subject}"


# =========================================================
# Correspondence Recipients
# =========================================================

class CorrespondenceRecipient(UUIDTimeStampedModel):
    """
    گیرندگان داخلی نامه.
    امکان تعیین شعبه، واحد یا کارمند وجود دارد.
    """

    correspondence = models.ForeignKey(
        SecretariatCorrespondence,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="نامه",
    )

    branch = models.ForeignKey(
        "Organization_APP.OrganizationBranch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="received_correspondences",
        verbose_name="شعبه گیرنده",
    )

    organizational_unit = models.ForeignKey(
        "Organization_APP.OrganizationalUnit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="received_correspondences",
        verbose_name="واحد گیرنده",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_received_correspondences",
        verbose_name="کارمند گیرنده",
    )

    is_copy = models.BooleanField(
        default=False,
        verbose_name="رونوشت",
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="خوانده‌شده",
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان مطالعه",
    )

    class Meta:
        verbose_name = "گیرنده نامه"
        verbose_name_plural = "گیرندگان نامه"
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["branch", "is_read"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(branch__isnull=False)
                    | Q(organizational_unit__isnull=False)
                    | Q(user__isnull=False)
                ),
                name="correspondence_recipient_has_target",
            ),
        ]

    def __str__(self):
        return f"گیرنده نامه {self.correspondence_id}"


# =========================================================
# Correspondence Attachments
# =========================================================

def correspondence_attachment_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return (
        f"secretariat/correspondence/"
        f"{instance.correspondence_id}/"
        f"{uuid.uuid4().hex}.{extension}"
    )


class CorrespondenceAttachment(UUIDTimeStampedModel):
    """
    فایل‌های پیوست نامه.
    نام اصلی فایل در مسیر ذخیره‌سازی استفاده نمی‌شود.
    """

    correspondence = models.ForeignKey(
        SecretariatCorrespondence,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="نامه",
    )

    file = models.FileField(
        upload_to=correspondence_attachment_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf", "png", "jpg", "jpeg",
                    "doc", "docx", "xls", "xlsx",
                    "txt", "zip",
                ]
            )
        ],
        verbose_name="فایل",
    )

    original_name = models.CharField(
        max_length=255,
        verbose_name="نام اصلی فایل",
    )

    description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="توضیحات",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="secretariat_uploaded_attachments",
        verbose_name="بارگذاری‌کننده",
    )

    class Meta:
        verbose_name = "پیوست نامه"
        verbose_name_plural = "پیوست‌های نامه"

    def __str__(self):
        return self.original_name


# =========================================================
# Correspondence Actions / Routing
# =========================================================

class CorrespondenceAction(UUIDTimeStampedModel):
    """
    گردش و اقدامات انجام‌شده روی نامه.
    """

    correspondence = models.ForeignKey(
        SecretariatCorrespondence,
        on_delete=models.CASCADE,
        related_name="actions",
        verbose_name="نامه",
    )

    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        db_index=True,
        verbose_name="نوع اقدام",
    )

    status = models.CharField(
        max_length=20,
        choices=ActionStatus.choices,
        default=ActionStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت اقدام",
    )

    source_branch = models.ForeignKey(
        "Organization_APP.OrganizationBranch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_actions_sent",
        verbose_name="شعبه مبدأ",
    )

    destination_branch = models.ForeignKey(
        "Organization_APP.OrganizationBranch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_actions_received",
        verbose_name="شعبه مقصد",
    )

    destination_unit = models.ForeignKey(
        "Organization_APP.OrganizationalUnit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_actions_received",
        verbose_name="واحد مقصد",
    )

    destination_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secretariat_actions_received",
        verbose_name="کارمند مقصد",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="secretariat_actions_performed",
        verbose_name="اقدام‌کننده",
    )

    description = models.TextField(
        blank=True,
        verbose_name="شرح اقدام",
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="مهلت انجام",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تکمیل",
    )

    class Meta:
        verbose_name = "اقدام و ارجاع نامه"
        verbose_name_plural = "اقدامات و ارجاعات نامه"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["destination_user", "status"]),
            models.Index(fields=["destination_unit", "status"]),
            models.Index(fields=["destination_branch", "status"]),
        ]

    def clean(self):
        super().clean()

        if not any([
            self.destination_branch_id,
            self.destination_unit_id,
            self.destination_user_id,
        ]):
            raise ValidationError(
                "برای ارجاع نامه باید حداقل یک مقصد تعیین شود."
            )

        organization_id = self.correspondence.secretariat.organization_id

        if self.destination_branch_id:
            if self.destination_branch.organization_id != organization_id:
                raise ValidationError({
                    "destination_branch": "شعبه مقصد متعلق به این سازمان نیست."
                })


# =========================================================
# Correspondence Status History
# =========================================================

class CorrespondenceHistory(UUIDTimeStampedModel):
    """
    تاریخچه تغییر وضعیت و رویدادهای نامه.
    رکوردهای این مدل باید از طریق سرویس ایجاد شوند
    و برای کاربران عادی قابل ویرایش یا حذف نباشند.
    """

    correspondence = models.ForeignKey(
        SecretariatCorrespondence,
        on_delete=models.PROTECT,
        related_name="history",
        verbose_name="نامه",
    )

    previous_status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        blank=True,
        verbose_name="وضعیت قبلی",
    )

    new_status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        verbose_name="وضعیت جدید",
    )

    description = models.TextField(
        blank=True,
        verbose_name="شرح تغییر",
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="secretariat_correspondence_history",
        verbose_name="تغییردهنده",
    )

    class Meta:
        verbose_name = "تاریخچه نامه"
        verbose_name_plural = "تاریخچه مکاتبات"
        ordering = ["-created_at"]


# =========================================================
# Internal Chat - Conversations
# =========================================================

class InternalConversation(UUIDTimeStampedModel):
    """
    گفتگوی داخلی کارکنان.
    این بخش مستقل از چت مشتریان در Ticket_APP است.
    """

    secretariat = models.ForeignKey(
        Secretariat,
        on_delete=models.PROTECT,
        related_name="conversations",
        verbose_name="دبیرخانه سازمان",
    )

    conversation_type = models.CharField(
        max_length=20,
        choices=ConversationType.choices,
        default=ConversationType.PRIVATE,
        db_index=True,
        verbose_name="نوع گفتگو",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان گفتگو",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    status = models.CharField(
        max_length=20,
        choices=ConversationStatus.choices,
        default=ConversationStatus.ACTIVE,
        db_index=True,
        verbose_name="وضعیت",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_internal_conversations",
        verbose_name="ایجادکننده",
    )

    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="زمان آخرین پیام",
    )

    class Meta:
        verbose_name = "گفتگوی داخلی"
        verbose_name_plural = "گفتگوهای داخلی"
        ordering = ["-last_message_at", "-created_at"]
        indexes = [
            models.Index(fields=["secretariat", "status"]),
        ]

    def clean(self):
        super().clean()

        if (
            self.conversation_type == ConversationType.GROUP
            and not self.title.strip()
        ):
            raise ValidationError({
                "title": "برای گفتگوی گروهی عنوان الزامی است."
            })

    def __str__(self):
        return self.title or f"گفتگوی {self.pk}"


# =========================================================
# Internal Chat - Members
# =========================================================

class InternalConversationMember(UUIDTimeStampedModel):
    """
    اعضای هر گفتگوی داخلی.
    دسترسی به گفتگو فقط برای اعضای مجاز خواهد بود.
    """

    conversation = models.ForeignKey(
        InternalConversation,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="گفتگو",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="internal_conversation_memberships",
        verbose_name="کارمند",
    )

    is_admin = models.BooleanField(
        default=False,
        verbose_name="مدیر گفتگو",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="عضویت فعال",
    )

    joined_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="زمان عضویت",
    )

    left_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان خروج",
    )

    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین زمان مطالعه",
    )

    class Meta:
        verbose_name = "عضو گفتگوی داخلی"
        verbose_name_plural = "اعضای گفتگوهای داخلی"
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "user"],
                name="uniq_internal_conversation_member",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.conversation}"


# =========================================================
# Internal Chat - Messages
# =========================================================

class InternalMessage(UUIDTimeStampedModel):
    """
    پیام‌های گفتگوی داخلی.
    """

    conversation = models.ForeignKey(
        InternalConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="گفتگو",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="internal_messages",
        verbose_name="فرستنده",
    )

    body = models.TextField(
        blank=True,
        verbose_name="متن پیام",
    )

    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="پاسخ به پیام",
    )

    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ویرایش",
    )

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="حذف‌شده",
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان حذف",
    )

    class Meta:
        verbose_name = "پیام داخلی"
        verbose_name_plural = "پیام‌های داخلی"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]

    def clean(self):
        super().clean()

        if not self.body.strip() and not self.pk:
            raise ValidationError(
                "متن پیام نمی‌تواند خالی باشد."
            )

        if self.reply_to_id:
            if self.reply_to.conversation_id != self.conversation_id:
                raise ValidationError({
                    "reply_to": "پیام مرجع باید متعلق به همین گفتگو باشد."
                })

    def __str__(self):
        return f"پیام {self.pk}"


# =========================================================
# Internal Chat - Message Attachments
# =========================================================

def internal_message_attachment_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return (
        f"secretariat/chat/"
        f"{instance.message.conversation_id}/"
        f"{uuid.uuid4().hex}.{extension}"
    )


class InternalMessageAttachment(UUIDTimeStampedModel):
    """
    پیوست پیام‌های داخلی.
    """

    message = models.ForeignKey(
        InternalMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="پیام",
    )

    file = models.FileField(
        upload_to=internal_message_attachment_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf", "png", "jpg", "jpeg",
                    "doc", "docx", "xls", "xlsx",
                    "txt", "zip",
                ]
            )
        ],
        verbose_name="فایل",
    )

    original_name = models.CharField(
        max_length=255,
        verbose_name="نام اصلی فایل",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="internal_message_attachments",
        verbose_name="بارگذاری‌کننده",
    )

    class Meta:
        verbose_name = "پیوست پیام"
        verbose_name_plural = "پیوست‌های پیام"

    def __str__(self):
        return self.original_name


# =========================================================
# Internal Chat - Read Receipts
# =========================================================

class InternalMessageReadReceipt(UUIDTimeStampedModel):
    """
    وضعیت خوانده‌شدن پیام توسط اعضای گفتگو.
    """

    message = models.ForeignKey(
        InternalMessage,
        on_delete=models.CASCADE,
        related_name="read_receipts",
        verbose_name="پیام",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="internal_message_read_receipts",
        verbose_name="کاربر",
    )

    read_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="زمان مطالعه",
    )

    class Meta:
        verbose_name = "رسید مطالعه پیام"
        verbose_name_plural = "رسیدهای مطالعه پیام"
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="uniq_internal_message_read_receipt",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "read_at"]),
        ]

    def clean(self):
        super().clean()

        if self.message_id and self.user_id:
            is_member = InternalConversationMember.objects.filter(
                conversation_id=self.message.conversation_id,
                user_id=self.user_id,
                is_active=True,
            ).exists()

            if not is_member:
                raise ValidationError(
                    "فقط اعضای فعال گفتگو می‌توانند پیام را مطالعه کنند."
                )

    def __str__(self):
        return f"{self.user} - {self.message}"
