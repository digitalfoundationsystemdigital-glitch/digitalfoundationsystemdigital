from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .permissions import (
    ACCOUNTANT_SECTIONS,
    ALL_SECTIONS,
    EMPLOYEE_SECTIONS,
    SECTION_ARCHIVE,
    SECTION_FINANCE,
    SECTION_HR,
    SECTION_PURCHASES,
    get_allowed_sections,
)


class RolePermissionTests(TestCase):
    def test_superuser_can_access_all_sections(self):
        user = User.objects.create_superuser("manager", password="pass")

        self.assertEqual(get_allowed_sections(user), ALL_SECTIONS)

    def test_accountant_group_can_access_accountant_sections(self):
        user = User.objects.create_user("user1", password="pass")
        group = Group.objects.create(name="محاسب")
        user.groups.add(group)

        self.assertEqual(get_allowed_sections(user), ACCOUNTANT_SECTIONS)
        self.assertIn(SECTION_FINANCE, get_allowed_sections(user))
        self.assertIn(SECTION_PURCHASES, get_allowed_sections(user))
        self.assertNotIn(SECTION_ARCHIVE, get_allowed_sections(user))
        self.assertNotIn(SECTION_HR, get_allowed_sections(user))

    def test_regular_user_gets_employee_sections_by_default(self):
        user = User.objects.create_user("employee", password="pass")

        self.assertEqual(get_allowed_sections(user), EMPLOYEE_SECTIONS)
        self.assertIn(SECTION_ARCHIVE, get_allowed_sections(user))
        self.assertNotIn(SECTION_FINANCE, get_allowed_sections(user))
        self.assertNotIn(SECTION_PURCHASES, get_allowed_sections(user))
        self.assertNotIn(SECTION_HR, get_allowed_sections(user))


class ViewPermissionTests(TestCase):
    def setUp(self):
        self.employee = User.objects.create_user("employee", password="pass")
        self.accountant = User.objects.create_user("accountant_user", password="pass")
        self.accountant.groups.add(Group.objects.create(name="محاسب"))
        self.manager = User.objects.create_superuser("manager", password="pass")

    def assertCanOpen(self, user, url_name):
        self.client.force_login(user)
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 200)

    def assertRedirectedFrom(self, user, url_name):
        self.client.force_login(user)
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_employee_view_access(self):
        self.assertCanOpen(self.employee, "dashboard")
        self.assertCanOpen(self.employee, "projects_list")
        self.assertCanOpen(self.employee, "customer_orders")
        self.assertCanOpen(self.employee, "customers_list")
        self.assertCanOpen(self.employee, "digital_archive")
        self.assertRedirectedFrom(self.employee, "purchases_list")
        self.assertRedirectedFrom(self.employee, "finance_summary")
        self.assertRedirectedFrom(self.employee, "hr_management")
        self.assertRedirectedFrom(self.employee, "reports_view")

    def test_accountant_view_access(self):
        self.assertCanOpen(self.accountant, "dashboard")
        self.assertCanOpen(self.accountant, "projects_list")
        self.assertCanOpen(self.accountant, "customer_orders")
        self.assertCanOpen(self.accountant, "customers_list")
        self.assertCanOpen(self.accountant, "purchases_list")
        self.assertCanOpen(self.accountant, "finance_summary")
        self.assertRedirectedFrom(self.accountant, "digital_archive")
        self.assertRedirectedFrom(self.accountant, "hr_management")
        self.assertRedirectedFrom(self.accountant, "reports_view")

    def test_system_manager_view_access(self):
        for url_name in (
            "dashboard",
            "projects_list",
            "customer_orders",
            "customers_list",
            "purchases_list",
            "finance_summary",
            "hr_management",
            "digital_archive",
            "reports_view",
        ):
            self.assertCanOpen(self.manager, url_name)


class AuthPageTests(TestCase):
    def test_auth_pages_open(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("employee_login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin_login")).status_code, 200)
