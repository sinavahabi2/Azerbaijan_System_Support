
import uuid

from django.db import models
from django.core.exceptions import ValidationError






class ServiceDetail(models.Model):

    class DeliveryType(models.TextChoices):
        REMOTE = "remote", "غیرحضوری"
        ONSITE = "onsite", "حضوری"
        HYBRID = "hybrid", "حضوری و غیرحضوری"

    class ServiceLevel(models.TextChoices):
        BASIC = "basic", "پایه"
        STANDARD = "standard", "استاندارد"
        PREMIUM = "premium", "ویژه"
        ENTERPRISE = "enterprise", "سازمانی"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    catalog_item = models.OneToOneField(
        "Catalog_APP.CatalogItem",
        on_delete=models.CASCADE,
        related_name="service_detail",
        verbose_name="خدمت",
    )

    delivery_type = models.CharField(
        max_length=20,
        choices=DeliveryType.choices,
        default=DeliveryType.HYBRID,
        verbose_name="نحوه ارائه خدمت",
    )

    service_level = models.CharField(
        max_length=20,
        choices=ServiceLevel.choices,
        default=ServiceLevel.STANDARD,
        verbose_name="سطح خدمت",
    )

    estimated_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="مدت زمان تخمینی (دقیقه)",
    )

    requires_appointment = models.BooleanField(
        default=False,
        verbose_name="نیازمند رزرو زمان",
    )

    requires_customer_presence = models.BooleanField(
        default=False,
        verbose_name="نیازمند حضور مشتری",
    )

    includes_support = models.BooleanField(
        default=False,
        verbose_name="دارای پشتیبانی",
    )

    support_duration_days = models.PositiveIntegerField(
        default=0,
        verbose_name="مدت پشتیبانی (روز)",
    )

    service_conditions = models.TextField(
        blank=True,
        verbose_name="شرایط ارائه خدمت",
    )

    service_scope = models.TextField(
        blank=True,
        verbose_name="محدوده خدمات",
    )

    exclusions = models.TextField(
        blank=True,
        verbose_name="موارد خارج از تعهد",
    )

    is_recurring = models.BooleanField(
        default=False,
        verbose_name="خدمت دوره‌ای",
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
        verbose_name="تاریخ ویرایش",
    )

    def clean(self):
        super().clean()

        if self.catalog_item_id:
            if self.catalog_item.item_type != "service":
                raise ValidationError({
                    "catalog_item": "فقط آیتم‌های از نوع خدمت قابل انتخاب هستند."
                })

        if not self.includes_support and self.support_duration_days:
            raise ValidationError({
                "support_duration_days": "مدت پشتیبانی بدون فعال بودن پشتیبانی باید صفر باشد."
            })

    class Meta:
        verbose_name = "مشخصات خدمت"
        verbose_name_plural = "مشخصات خدمات"

    def __str__(self):
        return f"مشخصات خدمت: {self.catalog_item.name}"


class ProductDetail(models.Model):

    class ProductCondition(models.TextChoices):
        NEW = "new", "نو"
        REFURBISHED = "refurbished", "بازسازی‌شده"
        USED = "used", "کارکرده"

    class WarrantyType(models.TextChoices):
        NONE = "none", "بدون گارانتی"
        MANUFACTURER = "manufacturer", "گارانتی سازنده"
        SELLER = "seller", "گارانتی فروشنده"
        THIRD_PARTY = "third_party", "گارانتی شرکت ثالث"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    catalog_item = models.OneToOneField(
        "Catalog_APP.CatalogItem",
        on_delete=models.CASCADE,
        related_name="product_detail",
        verbose_name="محصول",
    )

    model_number = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="شماره مدل",
    )

    manufacturer_part_number = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="کد فنی سازنده",
    )

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="بارکد",
    )

    condition = models.CharField(
        max_length=20,
        choices=ProductCondition.choices,
        default=ProductCondition.NEW,
        verbose_name="وضعیت محصول",
    )

    warranty_type = models.CharField(
        max_length=20,
        choices=WarrantyType.choices,
        default=WarrantyType.NONE,
        verbose_name="نوع گارانتی",
    )

    warranty_months = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="مدت گارانتی (ماه)",
    )

    warranty_description = models.TextField(
        blank=True,
        verbose_name="توضیحات گارانتی",
    )

    country_of_origin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="کشور سازنده",
    )

    package_contents = models.TextField(
        blank=True,
        verbose_name="محتویات بسته‌بندی",
    )

    technical_description = models.TextField(
        blank=True,
        verbose_name="توضیحات فنی",
    )

    requires_serial_number = models.BooleanField(
        default=False,
        verbose_name="نیازمند ثبت شماره سریال",
    )

    is_digital = models.BooleanField(
        default=False,
        verbose_name="محصول دیجیتالی",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ ویرایش",
    )

    def clean(self):
        super().clean()

        if self.catalog_item_id:
            if self.catalog_item.item_type != "product":
                raise ValidationError({
                    "catalog_item": "فقط آیتم‌های از نوع محصول قابل انتخاب هستند."
                })

        if self.warranty_type == self.WarrantyType.NONE:
            if self.warranty_months > 0:
                raise ValidationError({
                    "warranty_months": "برای محصول بدون گارانتی، مدت گارانتی باید صفر باشد."
                })

        elif self.warranty_months == 0:
            raise ValidationError({
                "warranty_months": "برای محصول دارای گارانتی، مدت گارانتی باید بیشتر از صفر باشد."
            })

    class Meta:
        verbose_name = "مشخصات محصول"
        verbose_name_plural = "مشخصات محصولات"

    def __str__(self):
        return f"مشخصات محصول: {self.catalog_item.name}"
