from django.db import models
from django.conf import settings


class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=150,
        verbose_name="نام وب‌سایت"
    )

    site_title = models.CharField(
        max_length=200,
        verbose_name="عنوان وب‌سایت"
    )

    site_description = models.TextField(
        blank=True,
        verbose_name="توضیحات وب‌سایت"
    )

    logo = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True,
        verbose_name="لوگوی وب‌سایت"
    )

    favicon = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True,
        verbose_name="آیکون وب‌سایت"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال بودن وب‌سایت"
    )

    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name="حالت تعمیر و نگهداری"
    )

    maintenance_message = models.TextField(
        blank=True,
        verbose_name="پیام حالت تعمیر و نگهداری"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "تنظیمات وب‌سایت"
        verbose_name_plural = "تنظیمات وب‌سایت"

    def __str__(self):
        return self.site_name


def save(self, *args, **kwargs):
    if not self.pk:
        existing = SiteSettings.objects.first()

        if existing:
            self.pk = existing.pk

    super().save(*args, **kwargs)


class SystemSettings(models.Model):
    LANGUAGE_CHOICES = [
        ("fa", "فارسی"),
        ("en", "English"),
    ]

    default_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="fa",
        verbose_name="زبان پیش‌فرض"
    )

    timezone = models.CharField(
        max_length=50,
        default="Asia/Tehran",
        verbose_name="منطقه زمانی"
    )

    items_per_page = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="تعداد رکورد در هر صفحه"
    )

    max_upload_size_mb = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="حداکثر حجم آپلود (MB)"
    )

    allow_registration = models.BooleanField(
        default=False,
        verbose_name="اجازه ثبت‌نام عمومی"
    )

    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name="فعال بودن اعلان‌ها"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "تنظیمات عمومی سامانه"
        verbose_name_plural = "تنظیمات عمومی سامانه"

    def save(self, *args, **kwargs):
        if not self.pk:
            existing = SystemSettings.objects.first()

            if existing:
                self.pk = existing.pk

        super().save(*args, **kwargs)

    def __str__(self):
        return "تنظیمات عمومی سامانه"


class ServerSettings(models.Model):
    ENVIRONMENT_CHOICES = [
        ("development", "توسعه"),
        ("testing", "آزمایش"),
        ("production", "عملیاتی"),
        ("backup", "پشتیبان"),
    ]

    name = models.CharField(
        max_length=150,
        verbose_name="نام سرور"
    )

    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default="development",
        verbose_name="محیط اجرا"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال بودن سرور"
    )

    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین بررسی"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "سرور"
        verbose_name_plural = "مدیریت سرورها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("login", "ورود کاربر"),
        ("logout", "خروج کاربر"),
        ("create", "ایجاد اطلاعات"),
        ("update", "ویرایش اطلاعات"),
        ("delete", "حذف اطلاعات"),
        ("system", "رویداد سیستمی"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="کاربر"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="نوع عملیات"
    )

    app_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام اپلیکیشن"
    )

    model_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام مدل"
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شناسه رکورد"
    )

    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="عنوان رکورد"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="جزئیات تغییرات"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        verbose_name = "گزارش فعالیت"
        verbose_name_plural = "گزارش فعالیت‌های سامانه"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.created_at}"


class Reports(AuditLog):
    class Meta:
        proxy = True
        verbose_name = "گزارش‌گیری"
        verbose_name_plural = "گزارش‌گیری"
