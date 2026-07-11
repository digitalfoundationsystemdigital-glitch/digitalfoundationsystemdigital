from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Employee


SECTION_DASHBOARD = "dashboard"
SECTION_PROJECTS = "projects"
SECTION_ORDERS = "orders"
SECTION_CUSTOMERS = "customers"
SECTION_PURCHASES = "purchases"
SECTION_FINANCE = "finance"
SECTION_HR = "hr"
SECTION_ARCHIVE = "archive"
SECTION_REPORTS = "reports"

ALL_SECTIONS = {
    SECTION_DASHBOARD,
    SECTION_PROJECTS,
    SECTION_ORDERS,
    SECTION_CUSTOMERS,
    SECTION_PURCHASES,
    SECTION_FINANCE,
    SECTION_HR,
    SECTION_ARCHIVE,
    SECTION_REPORTS,
}

EMPLOYEE_SECTIONS = {
    SECTION_DASHBOARD,
    SECTION_PROJECTS,
    SECTION_ORDERS,
    SECTION_CUSTOMERS,
    SECTION_ARCHIVE,
}

ACCOUNTANT_SECTIONS = {
    SECTION_DASHBOARD,
    SECTION_PROJECTS,
    SECTION_ORDERS,
    SECTION_CUSTOMERS,
    SECTION_PURCHASES,
    SECTION_FINANCE,
}

ROLE_SYSTEM_MANAGER = "system_manager"
ROLE_ACCOUNTANT = "accountant"
ROLE_EMPLOYEE = "employee"

SYSTEM_MANAGER_MARKERS = {
    "admin",
    "administrator",
    "system manager",
    "superuser",
    "مدير النظام",
}

ACCOUNTANT_MARKERS = {
    "accountant",
    "accounts",
    "finance",
    "financial",
    "محاسب",
    "الحسابات",
    "المالية",
    "الشؤون المالية",
}


def _normalized(value):
    return (value or "").strip().casefold()


def _user_group_names(user):
    if not user.is_authenticated:
        return []
    return [_normalized(name) for name in user.groups.values_list("name", flat=True)]


def _employee_position(user):
    if not user.is_authenticated:
        return ""
    return _normalized(
        Employee.objects.filter(user=user).values_list("position", flat=True).first()
    )


def _has_marker(values, markers):
    return any(marker in value for value in values for marker in markers)


def get_user_role(user):
    if not user.is_authenticated:
        return None

    group_names = _user_group_names(user)
    position = _employee_position(user)
    username = _normalized(user.username)

    identity_values = group_names + [position, username]
    if user.is_superuser or _has_marker(identity_values, SYSTEM_MANAGER_MARKERS):
        return ROLE_SYSTEM_MANAGER

    if _has_marker(identity_values, ACCOUNTANT_MARKERS):
        return ROLE_ACCOUNTANT

    return ROLE_EMPLOYEE


def get_allowed_sections(user):
    role = get_user_role(user)
    if role == ROLE_SYSTEM_MANAGER:
        return ALL_SECTIONS
    if role == ROLE_ACCOUNTANT:
        return ACCOUNTANT_SECTIONS
    if role == ROLE_EMPLOYEE:
        return EMPLOYEE_SECTIONS
    return set()


def can_access_section(user, section):
    return section in get_allowed_sections(user)


def section_required(section):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if can_access_section(request.user, section):
                return view_func(request, *args, **kwargs)

            messages.error(request, "لا تملك صلاحية الوصول إلى هذا القسم.")
            return redirect("dashboard")

        return wrapped

    return decorator


def permissions_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"allowed_sections": set(), "user_role": None}

    return {
        "allowed_sections": get_allowed_sections(user),
        "user_role": get_user_role(user),
    }
