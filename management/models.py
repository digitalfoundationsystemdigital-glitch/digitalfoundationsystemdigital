from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# 1. قسم إدارة المشاريع (المشاريع الكبرى للشركة)
class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المشروع")
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name="تصنيف المشروع")
    status = models.CharField(
        max_length=50, 
        choices=[('جاري العمل', 'جاري العمل'), ('مكتمل', 'مكتمل'), ('pending', 'قيد الانتظار')],
        default='pending',
        verbose_name="الحالة"
    )
    start_date = models.DateField(verbose_name="تاريخ البدء")
    image = models.ImageField(upload_to='projects/', null=True, blank=True, verbose_name="صورة المشروع")
    description = models.TextField(null=True, blank=True, verbose_name="وصف المشروع")

    def __str__(self):
        return self.name

# 2. قسم إدارة الزبائن
class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم الزبون")
    email = models.EmailField(verbose_name="البريد الإلكتروني", null=True, blank=True)
    phone = models.CharField(max_length=15, verbose_name="رقم الهاتف")

    def __str__(self):
        return self.name

# 3. قسم إدارة الطلبات (المهام اليومية والطلبات)
class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='orders', verbose_name="الزبون المسجل"
    )
    manual_customer_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="اسم الزبون (يدوي)")
    title = models.CharField(max_length=200, verbose_name="عنوان الطلب")
    item_name = models.CharField(max_length=100, verbose_name="الصنف/الخدمة") 
    description = models.TextField(verbose_name="وصف الطلب", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="الميزانية (د.ل)")
    deadline = models.DateField(null=True, blank=True, verbose_name="موعد التسليم")
    attachments = models.FileField(upload_to='order_attachments/', null=True, blank=True, verbose_name="المرفقات")

    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('processing', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('archived', 'مؤرشف'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="حالة الطلب")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الموظف المستلم")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.manual_customer_name or (self.customer.name if self.customer else "غير محدد")
        return f"{self.title} - {name}"

# 4. قسم المشتريات (المصاريف المرتبطة بالطلبات أو المكتب)
class Purchase(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='purchases', 
        null=True, blank=True, verbose_name="مرتبط بطلب"
    )
    item_name = models.CharField(max_length=200, verbose_name="الغرض")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="التكلفة")
    category = models.CharField(
        max_length=50, 
        choices=[('أجهزة', 'أجهزة'), ('برمجيات', 'برمجيات'), ('خدمات خارجية', 'خدمات خارجية'), ('أخرى', 'أخرى')],
        default='أخرى'
    )
    supplier = models.CharField(max_length=200, null=True, blank=True, verbose_name="المورد")
    date = models.DateField(verbose_name="تاريخ الشراء")
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.item_name} - {self.price} د.ل"

# 5. قسم الموارد البشرية (إدارة فريق العمل)
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="اسم الموظف")
    national_id = models.CharField(max_length=20, null=True, blank=True, verbose_name="الرقم الوطني")
    position = models.CharField(max_length=100, verbose_name="المسمى الوظيفي/التخصص")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المرتب الأساسي")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="رقم التواصل")
    is_active = models.BooleanField(default=True, verbose_name="على رأس العمل")
    joined_at = models.DateField(verbose_name="تاريخ التعيين")

    def __str__(self):
        return f"{self.name} ({self.position})"

# 6. قسم الشؤون المالية (الخزينة والتدفق المالي)
class Finance(models.Model):
    TYPE_CHOICES = [('income', 'إيراد (داخل)'), ('expense', 'مصروف (خارج)')]
    
    title = models.CharField(max_length=200, verbose_name="البيان")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المبلغ")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="نوع العملية")
    category = models.CharField(max_length=100, default="عام", verbose_name="التصنيف المالي")
    date = models.DateField(auto_now_add=True, verbose_name="التاريخ")
    
    # ربط اختياري لتعقب مصدر المال
    related_purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True)
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title} ({self.amount})"

# 7. قسم الأرشيف الرقمي (المستندات والملفات النهائية)
class DigitalArchive(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان الملف")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الطلب المرتبط")
    file = models.FileField(upload_to='archive/', verbose_name="الملف المؤرشف")
    file_type = models.CharField(max_length=50, choices=[('عقد', 'عقد'), ('تصميم', 'تصميم'), ('كود', 'برمجيات'), ('أخرى', 'أخرى')], default='أخرى')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
