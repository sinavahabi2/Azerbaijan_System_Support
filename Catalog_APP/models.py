
import uuid

from django.db import models, transaction


class CatalogCodeSequence(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    item_type = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="نوع آیتم",
    )

    next_number = models.PositiveIntegerField(
        default=1,
        verbose_name="شماره بعدی",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    PREFIXES = {
        "product": "PRD",
        "service": "SRV",
    }

    @classmethod
    def generate_code(cls, item_type):

        prefix = cls.PREFIXES.get(item_type)

        if not prefix:
            raise ValueError("نوع آیتم برای تولید کد معتبر نیست.")

        with transaction.atomic():

            sequence, created = cls.objects.get_or_create(
                item_type=item_type,
                defaults={"next_number": 1},
            )

            sequence = cls.objects.select_for_update().get(
                pk=sequence.pk
            )

            current_number = sequence.next_number

            sequence.next_number += 1

            sequence.save(
                update_fields=["next_number", "updated_at"]
            )

            return f"{prefix}-{current_number:06d}"

    class Meta:
        verbose_name = "شمارنده کد کاتالوگ"
        verbose_name_plural = "شمارنده‌های کد کاتالوگ"

    def __str__(self):
        return f"{self.item_type} - {self.next_number}"
