from django.contrib import admin


def configure_admin_site():
    admin.site.site_header = "منظومة المؤسسة الرقمية"
    admin.site.site_title = "إدارة النظام"
    admin.site.index_title = "لوحة الإدارة"
    admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser
