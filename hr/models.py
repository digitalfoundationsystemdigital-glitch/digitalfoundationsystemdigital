from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    NAME_CHOICES = [
        ('IT', 'تقنية المعلومات'),
        ('DEV', 'البرمجة'),
        ('SUPPORT', 'الدعم الفني'),
        ('CYBER', 'الأمن السيبراني'),
        ('ANALYST', 'تحليل النظم'),
        ('HR', 'الموارد البشرية'),
        ('FINANCE', 'المالية'),
        ('PURCHASING', 'المشتريات'),
    ]
    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=15, blank=True)
    job_title = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username