
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from Organization_APP.models import OrganizationMembership

User = get_user_model()

INITIAL_PASSWORD = "Aa@1234"


def create_employee_account(
    *,
    organization,
    employee_code,
    email,
    first_name="",
    last_name="",
):
    employee_code = str(employee_code).strip()
    email = str(email).strip().lower()

    if not employee_code.isdigit() or len(employee_code) != 10:
        raise ValidationError("کد ملی باید دقیقاً ۱۰ رقم باشد.")

    if not email:
        raise ValidationError("ایمیل پرسنل الزامی است.")

    if OrganizationMembership.objects.filter(
        organization=organization,
        employee_code=employee_code,
    ).exists():
        raise ValidationError(
            "این کد ملی قبلاً در این سازمان ثبت شده است."
        )

    user = User.objects.filter(username=employee_code).first()

    if user is None:
        user = User(
            username=employee_code,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        user.set_password(INITIAL_PASSWORD)
        user.save()

    else:
        if not user.is_active:
            raise ValidationError(
                "حساب کاربری موجود غیرفعال است."
            )

    return user
