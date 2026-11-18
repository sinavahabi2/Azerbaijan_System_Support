
from django import forms

from Organization_APP.models import OrganizationMembership


class OrganizationMembershipAdminForm(forms.ModelForm):
    first_name = forms.CharField(
        label="نام",
        max_length=150,
    )

    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=150,
    )

    email = forms.EmailField(
        label="ایمیل",
    )

    class Meta:
        model = OrganizationMembership
        fields = (
            "organization",
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "employment_type",
            "status",
            "start_date",
            "end_date",
            "notes",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance._state.adding:
            user = self.instance.user

            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def clean_employee_code(self):
        employee_code = self.cleaned_data["employee_code"].strip()

        if not employee_code.isdigit() or len(employee_code) != 10:
            raise forms.ValidationError(
                "کد ملی باید دقیقاً شامل ۱۰ رقم باشد."
            )

        return employee_code
