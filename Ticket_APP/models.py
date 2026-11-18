import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


def ticket_attachment_upload_to(instance, filename):
    """
    نام فایل اصلی در مسیر ذخیره‌سازی استفاده نمی‌شود.
    ذخیره‌سازی خصوصی و ارائه فایل از طریق view دارای مجوز باید در مرحله بعد تنظیم شود.
    """
    extension = Path(filename).suffix.lower()
    return f"private/tickets/{instance.ticket_id}/{uuid.uuid4().hex}{extension}"


def validate_attachment_size(file):
    max_size = 15 * 1024 * 1024  # 15 MB
    if file.size > max_size:
        raise ValidationError("حجم هر فایل پیوست نباید بیشتر از ۱۵ مگابایت باشد.")


class TicketBaseModel(models.Model):
    """مدل پایه برای شناسه UUID و زمان‌های ایجاد و ویرایش."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین ویرایش",
    )

    class Meta:
        abstract = True


class TicketCustomer(TicketBaseModel):
    class CustomerType(models.TextChoices):
        INDIVIDUAL = "individual", "شخص حقیقی"
        COMPANY = "company", "شخص حقوقی"

    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL,
        verbose_name="نوع مشتری",
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="نام",
    )
    last_name = models.CharField(
        max_length=120,
        verbose_name="نام خانوادگی",
    )
    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="نام شرکت",
    )
    mobile = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="شماره موبایل",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="یادداشت داخلی",
    )

    class Meta:
        verbose_name = "مشتری تیکت"
        verbose_name_plural = "مشتریان تیکت"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["mobile", "is_active"]),
        ]

    def clean(self):
        super().clean()

        if self.customer_type == self.CustomerType.COMPANY and not self.company_name.strip():
            raise ValidationError({
                "company_name": "برای مشتری حقوقی، نام شرکت الزامی است."
            })

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        if self.company_name:
            return f"{full_name} - {self.company_name}"
        return full_name


class TicketDepartment(TicketBaseModel):
    """
    صف یا واحد پاسخ‌گویی در یک سازمان.
    اتصال به OrganizationalUnit اختیاری است تا صف عمومی پشتیبانی هم ممکن باشد.
    """

    organization = models.ForeignKey(
        "Organization_APP.Organization",
        on_delete=models.PROTECT,
        related_name="ticket_departments",
        verbose_name="سازمان",
    )
    organizational_unit = models.ForeignKey(
        "Organization_APP.OrganizationalUnit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ticket_departments",
        verbose_name="واحد سازمانی مرتبط",
    )
    code = models.CharField(
        max_length=30,
        verbose_name="کد واحد پشتیبانی",
    )
    name = models.CharField(
        max_length=150,
        verbose_name="نام واحد پشتیبانی",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        verbose_name = "واحد پشتیبانی"
        verbose_name_plural = "واحدهای پشتیبانی"
        ordering = ["organization", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="ticket_department_code_per_org_uniq",
            ),
        ]

    def clean(self):
        super().clean()
        if self.organizational_unit_id and self.organization_id:
            if self.organizational_unit.organization_id != self.organization_id:
                raise ValidationError({
                    "organizational_unit": "واحد سازمانی باید متعلق به همین سازمان باشد."
                })

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class TicketCategory(TicketBaseModel):
    organization = models.ForeignKey(
        "Organization_APP.Organization",
        on_delete=models.PROTECT,
        related_name="ticket_categories",
        verbose_name="سازمان",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته‌بندی والد",
    )
    department = models.ForeignKey(
        TicketDepartment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="categories",
        verbose_name="واحد پیش‌فرض",
    )
    code = models.CharField(
        max_length=40,
        verbose_name="کد دسته‌بندی",
    )
    title = models.CharField(
        max_length=150,
        verbose_name="عنوان دسته‌بندی",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        verbose_name = "دسته‌بندی تیکت"
        verbose_name_plural = "دسته‌بندی‌های تیکت"
        ordering = ["organization", "sort_order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="ticket_category_code_per_org_uniq",
            ),
        ]

    def clean(self):
        super().clean()

        if self.department_id and self.department.organization_id != self.organization_id:
            raise ValidationError({
                "department": "واحد پشتیبانی باید متعلق به همین سازمان باشد."
            })

        if self.parent_id:
            if self.parent.organization_id != self.organization_id:
                raise ValidationError({
                    "parent": "دسته‌بندی والد باید متعلق به همین سازمان باشد."
                })
            if self.parent_id == self.pk:
                raise ValidationError({"parent": "یک دسته‌بندی نمی‌تواند والد خودش باشد."})

            ancestor = self.parent
            visited = set()
            while ancestor:
                if ancestor.pk == self.pk:
                    raise ValidationError({"parent": "ایجاد چرخه در دسته‌بندی‌ها مجاز نیست."})
                if ancestor.pk in visited:
                    raise ValidationError({"parent": "در زنجیره دسته‌بندی والد چرخه وجود دارد."})
                visited.add(ancestor.pk)
                ancestor = ancestor.parent

    def __str__(self):
        return f"{self.organization.name} - {self.title}"


class Ticket(TicketBaseModel):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        OPEN = "open", "باز"
        IN_PROGRESS = "in_progress", "در حال بررسی"
        WAITING_CUSTOMER = "waiting_customer", "در انتظار پاسخ مشتری"
        WAITING_INTERNAL = "waiting_internal", "در انتظار اقدام داخلی"
        RESOLVED = "resolved", "حل‌شده"
        CLOSED = "closed", "بسته‌شده"
        CANCELLED = "cancelled", "لغوشده"

    class Priority(models.TextChoices):
        LOW = "low", "کم"
        NORMAL = "normal", "عادی"
        HIGH = "high", "زیاد"
        URGENT = "urgent", "فوری"

    class Source(models.TextChoices):
        WEBSITE = "website", "وب‌سایت"
        PHONE = "phone", "تماس تلفنی"
        IN_PERSON = "in_person", "مراجعه حضوری"
        STAFF = "staff", "ثبت توسط کارمند"

    organization = models.ForeignKey(
        "Organization_APP.Organization",
        on_delete=models.PROTECT,
        related_name="support_tickets",
        verbose_name="سازمان مسئول",
    )
    branch = models.ForeignKey(
        "Organization_APP.OrganizationBranch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="support_tickets",
        verbose_name="شعبه مرتبط",
    )
    customer = models.ForeignKey(
        TicketCustomer,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="مشتری",
    )
    department = models.ForeignKey(
        TicketDepartment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
        verbose_name="واحد پشتیبانی فعلی",
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
        verbose_name="دسته‌بندی",
    )
    tracking_code = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="کد پیگیری",
    )
    subject = models.CharField(
        max_length=200,
        verbose_name="موضوع تیکت",
    )
    initial_message = models.TextField(
        verbose_name="شرح اولیه درخواست",
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        verbose_name="وضعیت",
    )
    priority = models.CharField(
        max_length=15,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
        verbose_name="اولویت",
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.WEBSITE,
        verbose_name="روش ثبت",
    )
    created_by_membership = models.ForeignKey(
        "Organization_APP.OrganizationMembership",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_support_tickets",
        verbose_name="کارمند ثبت‌کننده",
    )
    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان اولین پاسخ کارکنان",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان حل تیکت",
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان بستن تیکت",
    )
    last_activity_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="آخرین فعالیت",
    )
    customer_visible = models.BooleanField(
        default=True,
        verbose_name="قابل مشاهده برای مشتری",
    )

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
        ordering = ["-last_activity_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status", "priority"]),
            models.Index(fields=["department", "status", "last_activity_at"]),
            models.Index(fields=["customer", "created_at"]),
        ]

    def clean(self):
        super().clean()

        if self.branch_id and self.branch.organization_id != self.organization_id:
            raise ValidationError({
                "branch": "شعبه انتخاب‌شده متعلق به سازمان این تیکت نیست."
            })

        if self.department_id and self.department.organization_id != self.organization_id:
            raise ValidationError({
                "department": "واحد پشتیبانی متعلق به سازمان این تیکت نیست."
            })

        if self.category_id and self.category.organization_id != self.organization_id:
            raise ValidationError({
                "category": "دسته‌بندی متعلق به سازمان این تیکت نیست."
            })

        if (
            self.created_by_membership_id
            and self.created_by_membership.organization_id != self.organization_id
        ):
            raise ValidationError({
                "created_by_membership": "کارمند ثبت‌کننده باید عضو سازمان مسئول تیکت باشد."
            })

        if self.resolved_at and self.status not in {
            self.Status.RESOLVED, self.Status.CLOSED
        }:
            raise ValidationError({
                "resolved_at": "زمان حل فقط برای تیکت حل‌شده یا بسته‌شده ثبت می‌شود."
            })

    def __str__(self):
        return f"{self.tracking_code} - {self.subject}"


class TicketAccessCredential(TicketBaseModel):
    """
    اطلاعات احراز هویت مشتری برای یک تیکت.
    رمز خام هرگز در این مدل ذخیره نمی‌شود؛ فقط خروجی make_password().
    """

    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name="access_credential",
        verbose_name="تیکت",
    )
    secret_hash = models.CharField(
        max_length=256,
        editable=False,
        verbose_name="هش رمز محرمانه",
    )
    failed_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="تعداد تلاش ناموفق",
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان پایان محدودیت ورود",
    )
    last_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین احراز هویت موفق",
    )
    secret_changed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="زمان تغییر رمز",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "اعتبار دسترسی مشتری"
        verbose_name_plural = "اعتبارهای دسترسی مشتری"

    def __str__(self):
        return f"دسترسی مشتری - {self.ticket.tracking_code}"

    @property
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())


class TicketMessage(TicketBaseModel):
    class SenderType(models.TextChoices):
        CUSTOMER = "customer", "مشتری"
        EMPLOYEE = "employee", "کارمند"
        SYSTEM = "system", "سامانه"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "قابل مشاهده برای مشتری"
        INTERNAL = "internal", "یادداشت داخلی کارکنان"
        SYSTEM = "system", "پیام سیستمی"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="تیکت",
    )
    sender_type = models.CharField(
        max_length=15,
        choices=SenderType.choices,
        verbose_name="نوع فرستنده",
    )
    customer = models.ForeignKey(
        TicketCustomer,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sent_ticket_messages",
        verbose_name="مشتری فرستنده",
    )
    employee_membership = models.ForeignKey(
        "Organization_APP.OrganizationMembership",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sent_ticket_messages",
        verbose_name="کارمند فرستنده",
    )
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="پاسخ به پیام",
    )
    body = models.TextField(
        blank=True,
        verbose_name="متن پیام",
    )
    visibility = models.CharField(
        max_length=15,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
        verbose_name="سطح نمایش",
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name="ویرایش‌شده",
    )
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ویرایش",
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="حذف نرم",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان حذف",
    )

    class Meta:
        verbose_name = "پیام تیکت"
        verbose_name_plural = "پیام‌های تیکت"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "visibility", "created_at"]),
        ]

    def clean(self):
        super().clean()

        if not self.body.strip():
            raise ValidationError({"body": "متن پیام نمی‌تواند خالی باشد."})

        if self.sender_type == self.SenderType.CUSTOMER:
            if not self.customer_id or self.employee_membership_id:
                raise ValidationError(
                    "پیام مشتری باید فقط به مشتری فرستنده متصل باشد."
                )
            if self.customer_id != self.ticket.customer_id:
                raise ValidationError({
                    "customer": "فرستنده باید مشتری همین تیکت باشد."
                })
            if self.visibility != self.Visibility.PUBLIC:
                raise ValidationError({
                    "visibility": "پیام مشتری باید برای مشتری قابل مشاهده باشد."
                })

        elif self.sender_type == self.SenderType.EMPLOYEE:
            if not self.employee_membership_id or self.customer_id:
                raise ValidationError(
                    "پیام کارمند باید فقط به عضویت سازمانی فرستنده متصل باشد."
                )
            if self.employee_membership.organization_id != self.ticket.organization_id:
                raise ValidationError({
                    "employee_membership": "کارمند باید عضو سازمان مسئول تیکت باشد."
                })
            if self.visibility == self.Visibility.SYSTEM:
                raise ValidationError({
                    "visibility": "کارمند نمی‌تواند پیام سیستمی ثبت کند."
                })

        elif self.sender_type == self.SenderType.SYSTEM:
            if self.customer_id or self.employee_membership_id:
                raise ValidationError(
                    "پیام سیستمی نباید فرستنده مشتری یا کارمند داشته باشد."
                )
            if self.visibility != self.Visibility.SYSTEM:
                raise ValidationError({
                    "visibility": "پیام سیستمی باید سطح نمایش سیستمی داشته باشد."
                })

        if self.reply_to_id:
            if self.reply_to.ticket_id != self.ticket_id:
                raise ValidationError({
                    "reply_to": "پیام مرجع باید متعلق به همین تیکت باشد."
                })
            if (
                self.visibility == self.Visibility.INTERNAL
                and self.reply_to.visibility == self.Visibility.PUBLIC
            ):
                # مجاز است؛ یادداشت داخلی می‌تواند درباره پیام مشتری باشد.
                pass
            elif (
                self.visibility == self.Visibility.PUBLIC
                and self.reply_to.visibility == self.Visibility.INTERNAL
            ):
                raise ValidationError({
                    "reply_to": "پیام قابل مشاهده برای مشتری نمی‌تواند به یادداشت داخلی پاسخ دهد."
                })

    def __str__(self):
        return f"{self.ticket.tracking_code} - {self.get_sender_type_display()}"


class TicketAttachment(TicketBaseModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="تیکت",
    )
    message = models.ForeignKey(
        TicketMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
        verbose_name="پیام مرتبط",
    )
    file = models.FileField(
        upload_to=ticket_attachment_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf", "png", "jpg", "jpeg",
                    "doc", "docx", "xls", "xlsx",
                    "txt", "zip",
                ]
            ),
            validate_attachment_size,
        ],
        verbose_name="فایل",
    )
    original_name = models.CharField(
        max_length=255,
        verbose_name="نام اصلی فایل",
    )
    description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="توضیحات",
    )
    uploaded_by_customer = models.BooleanField(
        default=False,
        verbose_name="بارگذاری توسط مشتری",
    )
    uploaded_by_membership = models.ForeignKey(
        "Organization_APP.OrganizationMembership",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ticket_attachments",
        verbose_name="کارمند بارگذار",
    )
    is_customer_visible = models.BooleanField(
        default=True,
        verbose_name="قابل مشاهده برای مشتری",
    )

    class Meta:
        verbose_name = "پیوست تیکت"
        verbose_name_plural = "پیوست‌های تیکت"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
        ]

    def clean(self):
        super().clean()

        if self.message_id and self.message.ticket_id != self.ticket_id:
            raise ValidationError({
                "message": "پیام انتخاب‌شده متعلق به این تیکت نیست."
            })

        if self.uploaded_by_customer and self.uploaded_by_membership_id:
            raise ValidationError(
                "فایل نمی‌تواند هم‌زمان توسط مشتری و کارمند بارگذاری شده باشد."
            )

        if not self.uploaded_by_customer and not self.uploaded_by_membership_id:
            raise ValidationError(
                "بارگذار فایل باید مشتری یا کارمند مشخصی باشد."
            )

        if (
            self.uploaded_by_membership_id
            and self.uploaded_by_membership.organization_id != self.ticket.organization_id
        ):
            raise ValidationError({
                "uploaded_by_membership": "کارمند بارگذار باید عضو سازمان مسئول تیکت باشد."
            })

        if self.message_id:
            if self.uploaded_by_customer and self.message.sender_type != TicketMessage.SenderType.CUSTOMER:
                raise ValidationError("پیوست مشتری باید به پیام مشتری متصل باشد.")
            if self.uploaded_by_membership_id and self.message.sender_type != TicketMessage.SenderType.EMPLOYEE:
                raise ValidationError("پیوست کارمند باید به پیام کارمند متصل باشد.")

    def __str__(self):
        return self.original_name


class TicketAssignment(TicketBaseModel):
    """
    هر بار تخصیص یا انتقال یک رکورد جدید می‌سازد.
    رکورد فعال با ended_at=None مشخص می‌شود.
    """

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="تیکت",
    )
    department = models.ForeignKey(
        TicketDepartment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assignments",
        verbose_name="واحد مسئول",
    )
    assigned_to = models.ForeignKey(
        "Organization_APP.OrganizationMembership",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ticket_assignments",
        verbose_name="کارمند مسئول",
    )
    assigned_by = models.ForeignKey(
        "Organization_APP.OrganizationMembership",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_ticket_assignments",
        verbose_name="تخصیص‌دهنده",
    )
    note = models.TextField(
        blank=True,
        verbose_name="توضیح تخصیص یا انتقال",
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="زمان تخصیص",
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان پایان مسئولیت",
    )

    class Meta:
        verbose_name = "تخصیص تیکت"
        verbose_name_plural = "تخصیص‌ها و ارجاعات تیکت"
        ordering = ["-assigned_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["ticket"],
                condition=Q(ended_at__isnull=True),
                name="one_active_ticket_assignment",
            ),
        ]
        indexes = [
            models.Index(fields=["assigned_to", "ended_at"]),
            models.Index(fields=["department", "ended_at"]),
        ]

    def clean(self):
        super().clean()

        if not self.department_id and not self.assigned_to_id:
            raise ValidationError(
                "تخصیص باید حداقل به یک واحد یا یک کارمند انجام شود."
            )

        if self.department_id and self.department.organization_id != self.ticket.organization_id:
            raise ValidationError({
                "department": "واحد مسئول باید متعلق به سازمان تیکت باشد."
            })

        if self.assigned_to_id and self.assigned_to.organization_id != self.ticket.organization_id:
            raise ValidationError({
                "assigned_to": "کارمند مسئول باید عضو سازمان تیکت باشد."
            })

        if self.assigned_by_id and self.assigned_by.organization_id != self.ticket.organization_id:
            raise ValidationError({
                "assigned_by": "تخصیص‌دهنده باید عضو سازمان تیکت باشد."
            })

        if self.ended_at and self.ended_at < self.assigned_at:
            raise ValidationError({
                "ended_at": "زمان پایان مسئولیت نمی‌تواند قبل از زمان تخصیص باشد."
            })

    def __str__(self):
        target = self.assigned_to or self.department or "صف عمومی"
        return f"{self.ticket.tracking_code} - {target}"


class TicketStatusHistory(TicketBaseModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="تیکت",
    )
    previous_status = models.CharField(
        max_length=25,
        choices=Ticket.Status.choices,
        blank=True,
        verbose_name="وضعیت قبلی",
    )
    new_status = models.CharField(
        max_length=25,
        choices=Ticket.Status.choices,
        verbose_name="وضعیت جدید",
    )
    changed_by_membership = models.ForeignKey(
        "Organization_APP.OrganizationMembership",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ticket_status_changes",
        verbose_name="کارمند تغییر‌دهنده",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات تغییر",
    )
    changed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="زمان تغییر",
    )

    class Meta:
        verbose_name = "تاریخچه وضعیت تیکت"
        verbose_name_plural = "تاریخچه وضعیت تیکت‌ها"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(fields=["ticket", "changed_at"]),
        ]

    def clean(self):
        super().clean()
        if (
            self.changed_by_membership_id
            and self.changed_by_membership.organization_id != self.ticket.organization_id
        ):
            raise ValidationError({
                "changed_by_membership": "کارمند باید عضو سازمان مسئول تیکت باشد."
            })

    def __str__(self):
        return f"{self.ticket.tracking_code} - {self.get_new_status_display()}"


class TicketFeedback(TicketBaseModel):
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name="feedback",
        verbose_name="تیکت",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز مشتری",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="نظر مشتری",
    )
    submitted_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="زمان ثبت بازخورد",
    )

    class Meta:
        verbose_name = "بازخورد تیکت"
        verbose_name_plural = "بازخوردهای تیکت"
        ordering = ["-submitted_at"]

    def clean(self):
        super().clean()
        if self.ticket.status not in {Ticket.Status.RESOLVED, Ticket.Status.CLOSED}:
            raise ValidationError(
                "ثبت بازخورد فقط پس از حل یا بسته‌شدن تیکت امکان‌پذیر است."
            )

    def __str__(self):
        return f"{self.ticket.tracking_code} - امتیاز {self.rating}"
