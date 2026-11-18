import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Organization(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کد سازمان",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="نام سازمان",
    )

    legal_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="نام رسمی سازمان",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل سازمان",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="شماره تماس",
    )

    website = models.URLField(
        blank=True,
        verbose_name="وب‌سایت",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "سازمان"
        verbose_name_plural = "سازمان‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationBranch(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="branches",
        verbose_name="سازمان",
    )

    code = models.CharField(
        max_length=30,
        verbose_name="کد شعبه",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="نام شعبه",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    manager = models.ForeignKey(
        "OrganizationMembership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches",
        verbose_name="مسئول شعبه",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="شماره تماس",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل",
    )

    address = models.TextField(
        blank=True,
        verbose_name="نشانی",
    )

    is_headquarters = models.BooleanField(
        default=False,
        verbose_name="شعبه مرکزی",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "شعبه سازمان"
        verbose_name_plural = "شعب سازمان"
        ordering = ["organization", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_branch_code_per_organization",
            ),
            models.UniqueConstraint(
                fields=["organization"],
                condition=models.Q(is_headquarters=True),
                name="unique_headquarters_per_organization",
            ),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    def clean(self):
        super().clean()

        if self.manager_id and self.organization_id:
            if self.manager.organization_id != self.organization_id:
                raise ValidationError({
                    "manager": "مدیر شعبه باید عضو همان سازمان باشد."
                })


class OrganizationalUnit(models.Model):
    class UnitType(models.TextChoices):
        MANAGEMENT = "management", "مدیریت"
        DEPARTMENT = "department", "اداره"
        DIVISION = "division", "بخش"
        TEAM = "team", "گروه"
        OTHER = "other", "سایر"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="organizational_units",
        verbose_name="سازمان",
    )

    branch = models.ForeignKey(
        OrganizationBranch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organizational_units",
        verbose_name="شعبه",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="واحد بالادستی",
    )

    code = models.CharField(
        max_length=30,
        verbose_name="کد واحد",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="نام واحد",
    )

    unit_type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.DEPARTMENT,
        verbose_name="نوع واحد",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    manager = models.ForeignKey(
        "OrganizationMembership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_units",
        verbose_name="مسئول واحد",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "واحد سازمانی"
        verbose_name_plural = "واحدهای سازمانی"
        ordering = ["organization", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_unit_code_per_organization",
            ),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    def clean(self):
        super().clean()

        if self.branch_id and self.organization_id:
            if self.branch.organization_id != self.organization_id:
                raise ValidationError({
                    "branch": "شعبه انتخاب‌شده متعلق به این سازمان نیست."
                })

        if self.manager_id and self.organization_id:
            if self.manager.organization_id != self.organization_id:
                raise ValidationError({
                    "manager": "مدیر واحد باید عضو همان سازمان باشد."
                })

        if not self.parent_id:
            return

        if self.parent_id == self.pk:
            raise ValidationError({
                "parent": "یک واحد نمی‌تواند والد خودش باشد."
            })

        if self.parent.organization_id != self.organization_id:
            raise ValidationError({
                "parent": "واحد والد باید متعلق به همان سازمان باشد."
            })

        if self.parent.branch_id != self.branch_id:
            raise ValidationError({
                "parent": "واحد والد و فرزند باید متعلق به یک شعبه باشند."
            })

        ancestor = self.parent
        visited = set()

        while ancestor is not None:
            if ancestor.pk == self.pk:
                raise ValidationError({
                    "parent": "ایجاد چرخه در ساختار واحدهای سازمانی مجاز نیست."
                })

            if ancestor.pk in visited:
                raise ValidationError({
                    "parent": "در ساختار والدین واحدهای سازمانی چرخه‌ی قبلی وجود دارد."
                })

            visited.add(ancestor.pk)
            ancestor = ancestor.parent


class JobPosition(models.Model):
    class PositionLevel(models.TextChoices):
        EXECUTIVE = "executive", "مدیریت ارشد"
        MANAGER = "manager", "مدیریت"
        SUPERVISOR = "supervisor", "سرپرستی"
        SPECIALIST = "specialist", "کارشناسی"
        STAFF = "staff", "کارمندی"
        OTHER = "other", "سایر"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="job_positions",
        verbose_name="سازمان",
    )

    code = models.CharField(
        max_length=30,
        verbose_name="کد سمت",
    )

    title = models.CharField(
        max_length=150,
        verbose_name="عنوان سمت",
    )

    level = models.CharField(
        max_length=20,
        choices=PositionLevel.choices,
        default=PositionLevel.OTHER,
        verbose_name="سطح سازمانی",
    )

    description = models.TextField(
        blank=True,
        verbose_name="شرح وظایف",
    )

    is_managerial = models.BooleanField(
        default=False,
        verbose_name="سمت مدیریتی",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "سمت سازمانی"
        verbose_name_plural = "سمت‌های سازمانی"
        ordering = ["organization", "level", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_position_code_per_organization",
            ),
        ]

    def __str__(self):
        return self.title


class OrganizationMembership(models.Model):
    class MembershipStatus(models.TextChoices):
        PENDING = "pending", "در انتظار تأیید"
        ACTIVE = "active", "فعال"
        SUSPENDED = "suspended", "تعلیق‌شده"
        TERMINATED = "terminated", "پایان همکاری"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "تمام‌وقت"
        PART_TIME = "part_time", "پاره‌وقت"
        CONTRACT = "contract", "قراردادی"
        TEMPORARY = "temporary", "موقت"
        OTHER = "other", "سایر"

    must_change_password = models.BooleanField(
        default=True,
        verbose_name="الزام تغییر رمز عبور در اولین ورود",
    )
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="memberships",
        verbose_name="سازمان",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organization_memberships",
        verbose_name="حساب کاربری",
    )

    employee_code = models.CharField(
        max_length=50,
        verbose_name="کد پرسنلی",
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        verbose_name="نوع همکاری",
    )

    status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.PENDING,
        verbose_name="وضعیت عضویت",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع همکاری",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان همکاری",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="توضیحات",
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
        verbose_name = "عضویت سازمانی"
        verbose_name_plural = "عضویت‌های سازمانی"
        ordering = ["organization", "employee_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_user_membership_per_organization",
            ),
            models.UniqueConstraint(
                fields=["organization", "employee_code"],
                name="unique_employee_code_per_organization",
            ),
        ]

    def clean(self):
        super().clean()

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    "end_date": "تاریخ پایان همکاری نمی‌تواند قبل از تاریخ شروع باشد."
                })

    def __str__(self):
        return f"{self.organization.name} - {self.employee_code}"


class PositionAssignment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    membership = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.PROTECT,
        related_name="position_assignments",
        verbose_name="عضویت سازمانی",
    )

    position = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name="سمت سازمانی",
    )

    organizational_unit = models.ForeignKey(
        OrganizationalUnit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="position_assignments",
        verbose_name="واحد سازمانی",
    )

    branch = models.ForeignKey(
        OrganizationBranch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="position_assignments",
        verbose_name="شعبه",
    )

    is_primary = models.BooleanField(
        default=False,
        verbose_name="سمت اصلی",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع مسئولیت",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان مسئولیت",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
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
        verbose_name = "انتصاب سازمانی"
        verbose_name_plural = "انتصاب‌های سازمانی"
        ordering = ["membership", "-is_primary", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["membership"],
                condition=models.Q(
                    is_primary=True,
                    is_active=True,
                ),
                name="unique_active_primary_position_per_member",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.membership_id:
            return

        organization_id = self.membership.organization_id

        if self.position_id:
            if self.position.organization_id != organization_id:
                raise ValidationError({
                    "position": "سمت انتخاب‌شده متعلق به سازمان کارمند نیست."
                })

        if self.organizational_unit_id:
            if self.organizational_unit.organization_id != organization_id:
                raise ValidationError({
                    "organizational_unit": "واحد انتخاب‌شده متعلق به سازمان کارمند نیست."
                })

        if self.branch_id:
            if self.branch.organization_id != organization_id:
                raise ValidationError({
                    "branch": "شعبه انتخاب‌شده متعلق به سازمان کارمند نیست."
                })

        if (
            self.organizational_unit_id
            and self.branch_id
            and self.organizational_unit.branch_id
            and self.organizational_unit.branch_id != self.branch_id
        ):
            raise ValidationError({
                "branch": "شعبه انتساب باید با شعبه واحد سازمانی مطابقت داشته باشد."
            })

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    "end_date": "تاریخ پایان مسئولیت نمی‌تواند قبل از تاریخ شروع باشد."
                })

    def __str__(self):
        return f"{self.membership} - {self.position.title}"


class ReportingLine(models.Model):
    class RelationshipType(models.TextChoices):
        PRIMARY = "primary", "مدیر مستقیم"
        FUNCTIONAL = "functional", "مدیر وظیفه‌ای"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    subordinate = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.PROTECT,
        related_name="reporting_lines",
        verbose_name="کارمند",
    )

    manager = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.PROTECT,
        related_name="managed_reporting_lines",
        verbose_name="مدیر",
    )

    relationship_type = models.CharField(
        max_length=20,
        choices=RelationshipType.choices,
        default=RelationshipType.PRIMARY,
        verbose_name="نوع ارتباط",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
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
        verbose_name = "ارتباط گزارش‌دهی"
        verbose_name_plural = "ارتباطات گزارش‌دهی"
        ordering = ["subordinate", "relationship_type"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(manager=models.F("subordinate")),
                name="reporting_line_no_self_management",
            ),
            models.UniqueConstraint(
                fields=["subordinate"],
                condition=models.Q(
                    relationship_type="primary",
                    is_active=True,
                ),
                name="unique_active_primary_manager",
            ),
            models.UniqueConstraint(
                fields=["subordinate", "manager", "relationship_type"],
                condition=models.Q(is_active=True),
                name="unique_active_reporting_relationship",
            ),
        ]

    def clean(self):
        super().clean()

        if self.subordinate_id and self.manager_id:
            if self.subordinate_id == self.manager_id:
                raise ValidationError(
                    "یک کارمند نمی‌تواند مدیر خودش باشد."
                )

            if (
                self.subordinate.organization_id
                != self.manager.organization_id
            ):
                raise ValidationError(
                    "کارمند و مدیر باید عضو یک سازمان باشند."
                )

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد."
            )

        if not (
            self.is_active
            and self.subordinate_id
            and self.manager_id
        ):
            return

        # بررسی چرخه با پیمایش تمام روابط مدیریتی فعال
        # جهت یال‌ها: کارمند -> مدیر
        pending = [self.manager_id]
        visited = set()

        while pending:
            current_id = pending.pop()

            if current_id == self.subordinate_id:
                raise ValidationError(
                    "ایجاد چرخه در سلسله‌مراتب مدیریتی مجاز نیست."
                )

            if current_id in visited:
                continue

            visited.add(current_id)

            manager_ids = ReportingLine.objects.filter(
                subordinate_id=current_id,
                is_active=True,
            ).exclude(
                pk=self.pk,
            ).values_list(
                "manager_id",
                flat=True,
            )

            pending.extend(manager_ids)

    def __str__(self):
        return f"{self.subordinate} ← {self.manager}"


class OrganizationChart(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشرشده"
        ARCHIVED = "archived", "بایگانی‌شده"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="charts",
        verbose_name="سازمان",
    )

    version = models.PositiveIntegerField(
        verbose_name="شماره نسخه",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان چارت سازمانی",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )

    effective_from = models.DateField(
        verbose_name="تاریخ شروع اعتبار",
    )

    effective_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان اعتبار",
    )

    is_current = models.BooleanField(
        default=False,
        verbose_name="نسخه جاری",
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ انتشار",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "چارت سازمانی"
        verbose_name_plural = "چارت‌های سازمانی"
        ordering = ["organization", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "version"],
                name="unique_chart_version_per_organization",
            ),
            models.UniqueConstraint(
                fields=["organization"],
                condition=models.Q(is_current=True),
                name="unique_current_chart_per_organization",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.effective_until
            and self.effective_until < self.effective_from
        ):
            raise ValidationError(
                "تاریخ پایان اعتبار نمی‌تواند قبل از تاریخ شروع باشد."
            )

        if self.is_current and self.status != self.Status.PUBLISHED:
            raise ValidationError(
                "فقط چارت منتشرشده می‌تواند نسخه جاری باشد."
            )

        if self.status == self.Status.ARCHIVED and self.is_current:
            raise ValidationError(
                "چارت بایگانی‌شده نمی‌تواند نسخه جاری باشد."
            )

        if self.is_current and self.effective_until:
            from django.utils import timezone

            if self.effective_until < timezone.localdate():
                raise ValidationError(
                    "چارت منقضی‌شده نمی‌تواند نسخه جاری باشد."
                )

    def __str__(self):
        return (
            f"{self.organization.name} - {self.title} "
            f"- نسخه {self.version}"
        )


class OrganizationChartNode(models.Model):
    class NodeType(models.TextChoices):
        UNIT = "unit", "واحد سازمانی"
        POSITION = "position", "سمت سازمانی"
        EMPLOYEE = "employee", "کارمند"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه",
    )

    chart = models.ForeignKey(
        OrganizationChart,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name="چارت سازمانی",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="گره والد",
    )

    node_type = models.CharField(
        max_length=20,
        choices=NodeType.choices,
        verbose_name="نوع گره",
    )

    organizational_unit = models.ForeignKey(
        OrganizationalUnit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="chart_nodes",
        verbose_name="واحد سازمانی",
    )

    position = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="chart_nodes",
        verbose_name="سمت سازمانی",
    )

    membership = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="chart_nodes",
        verbose_name="کارمند",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان نمایشی",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات تکمیلی",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "گره چارت سازمانی"
        verbose_name_plural = "گره‌های چارت سازمانی"
        ordering = ["sort_order", "created_at"]

    def clean(self):
        super().clean()

        references = {
            self.NodeType.UNIT: self.organizational_unit,
            self.NodeType.POSITION: self.position,
            self.NodeType.EMPLOYEE: self.membership,
        }

        selected = [
            self.organizational_unit,
            self.position,
            self.membership,
        ]

        if self.node_type not in references:
            raise ValidationError({
                "node_type": "نوع گره معتبر نیست."
            })

        if sum(item is not None for item in selected) != 1:
            raise ValidationError(
                "هر گره باید دقیقاً به یک واحد، سمت یا کارمند متصل باشد."
            )

        if references[self.node_type] is None:
            raise ValidationError(
                "نوع گره با عنصر انتخاب‌شده مطابقت ندارد."
            )

        if any(
            item is not None
            for key, item in zip(references.keys(), selected)
            if key != self.node_type
        ):
            raise ValidationError(
                "نوع گره با اطلاعات انتخاب‌شده مطابقت ندارد."
            )

        if self.chart_id:
            organization_id = self.chart.organization_id

            for item in selected:
                if (
                    item is not None
                    and item.organization_id != organization_id
                ):
                    raise ValidationError(
                        "عنصر انتخاب‌شده متعلق به سازمان این چارت نیست."
                    )

        if not self.parent_id:
            return

        if self.parent_id == self.pk:
            raise ValidationError({
                "parent": "یک گره نمی‌تواند والد خودش باشد."
            })

        if self.parent.chart_id != self.chart_id:
            raise ValidationError({
                "parent": "گره والد باید متعلق به همان چارت باشد."
            })

        ancestor = self.parent
        visited = set()

        while ancestor is not None:
            if ancestor.pk == self.pk:
                raise ValidationError({
                    "parent": "ایجاد چرخه در ساختار چارت سازمانی مجاز نیست."
                })

            if ancestor.pk in visited:
                raise ValidationError({
                    "parent": "در زنجیره والدین این چارت چرخه‌ی قبلی وجود دارد."
                })

            visited.add(ancestor.pk)
            ancestor = ancestor.parent

    def __str__(self):
        return self.title or self.get_node_type_display()