from django.urls import path
from . import views

urlpatterns = [
    # الصفحة الرئيسية للوحة التحكم (التقارير والإحصائيات)
    path('', views.dashboard, name='dashboard'),

    # 1. قسم إدارة المشاريع (عرض، إضافة، حذف، تعديل)
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('projects/edit/<int:pk>/', views.edit_project, name='edit_project'),
    
    # 2. قسم إدارة الطلبات (النظام الداخلي)
    path('orders/', views.customer_orders, name='customer_orders'),
    
    # مسار تحديث الحالة (بدء التنفيذ / تم الإنجاز) لتعمل الأزرار الملونة
    path('orders/update-status/<int:pk>/<str:status>/', views.update_order_status, name='update_order_status'),
    
    # مسار التعديل (لكي يعمل زر "تعديل" في بطاقة الطلب)
    path('orders/edit/<int:pk>/', views.edit_order, name='edit_order'),
    
    # مسار الحذف/الأرشفة (لكي يعمل زر "مؤرشف" في بطاقة الطلب)
    path('orders/delete/<int:pk>/', views.delete_order, name='delete_order'),

    # 3. قسم إدارة الزبائن (المطور)
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'), # المسار الذي كان ناقصاً
    path('customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'), # مسار حذف الزبون

    # 4. قسم الموارد البشرية (الموظفين)
    path('hr/', views.hr_management, name='hr_management'),
    path('hr/employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
    path('hr/employees/<int:pk>/delete/', views.delete_employee, name='delete_employee'),

    # 5. قسم المالية (الشؤون المالية)
    path('finance/', views.finance_summary, name='finance_summary'),

    # 6. قسم المشتريات
    path('purchases/', views.purchases_list, name='purchases_list'),

    # 7. قسم الأرشيف الرقمي
    path('archive/', views.digital_archive, name='digital_archive'),

    # 8. قسم التقارير والإحصائيات
    path('reports/', views.reports_view, name='reports_view'),
]
