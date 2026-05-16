from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

# استيراد كافة الجداول المطورة
from .models import Project, Customer, Order, Employee, Finance, Purchase, DigitalArchive

# --- 0. لوحة التحكم الرئيسية ---
@login_required
def dashboard(request):
    context = {
        'projects_count': Project.objects.count(), 
        'orders_count': Order.objects.count(), 
        'employees_count': Employee.objects.count(), 
        'customers_count': Customer.objects.count(), 
        'total_finance': Finance.objects.aggregate(Sum('amount'))['amount__sum'] or 0, 
        'archives_count': DigitalArchive.objects.count(), 
    }
    return render(request, 'dashboard.html', context)

# --- 1. قسم إدارة المشاريع ---
@login_required
def projects_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        category = request.POST.get('category')
        start_date = request.POST.get('start_date')
        status = request.POST.get('status')
        description = request.POST.get('description')
        image = request.FILES.get('project_image')
        
        Project.objects.create(
            name=name, category=category, start_date=start_date, 
            status=status, description=description, image=image
        )
        messages.success(request, "تم إضافة المشروع بنجاح")
        return redirect('projects_list')

    projects = Project.objects.all().order_by('-start_date')
    return render(request, 'projects.html', {'projects': projects})

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.name = request.POST.get('name')
        project.category = request.POST.get('category')
        project.status = request.POST.get('status')
        project.start_date = request.POST.get('start_date')
        project.description = request.POST.get('description')
        if request.FILES.get('project_image'):
            project.image = request.FILES.get('project_image')
        project.save()
        messages.success(request, "تم تحديث المشروع بنجاح")
        return redirect('projects_list')
    return render(request, 'edit_project.html', {'project': project})

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.warning(request, "تم حذف المشروع")
    return redirect('projects_list')

# --- 2. قسم إدارة الطلبات ---
@login_required
def customer_orders(request):
    if request.method == "POST":
        manual_name = request.POST.get('manual_customer_name')
        title = request.POST.get('title')
        item_name = request.POST.get('item_name')
        description = request.POST.get('description')
        
        raw_price = request.POST.get('price')
        price = float(raw_price) if raw_price and raw_price.strip() else 0.00
        
        deadline = request.POST.get('deadline')
        attachments = request.FILES.get('attachments')

        Order.objects.create(
            manual_customer_name=manual_name,
            title=title,
            item_name=item_name,
            description=description,
            price=price,
            deadline=deadline if deadline and deadline.strip() else None,
            attachments=attachments,
            status='new',
            recorded_by=request.user
        )
        messages.success(request, "تم تسجيل المهمة بنجاح")
        return redirect('customer_orders')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def update_order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)
    order.status = status 
    order.save()
    messages.info(request, f"تم تحديث الحالة: {order.get_status_display()}")
    return redirect('customer_orders')

@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.manual_customer_name = request.POST.get('manual_customer_name')
        order.title = request.POST.get('title')
        order.item_name = request.POST.get('item_name')
        
        raw_price = request.POST.get('price')
        order.price = float(raw_price) if raw_price and raw_price.strip() else 0.00
        
        deadline = request.POST.get('deadline')
        order.deadline = deadline if deadline and deadline.strip() else None
        
        if request.FILES.get('attachments'):
            order.attachments = request.FILES.get('attachments')
            
        order.save()
        messages.success(request, "تم تحديث بيانات المهمة")
        return redirect('customer_orders')
    return render(request, 'edit_order.html', {'order': order})

@login_required
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.warning(request, "تم حذف المهمة")
    return redirect('customer_orders')

# --- 3. قسم إدارة الزبائن ---
@login_required
def customers_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        Customer.objects.create(name=name, email=email, phone=phone)
        messages.success(request, "تم إضافة الزبون بنجاح")
        return redirect('customers_list')

    customers = Customer.objects.all().order_by('name')
    return render(request, 'customers.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer_orders = Order.objects.filter(manual_customer_name=customer.name).order_by('-created_at')
    context = {
        'customer': customer,
        'orders': customer_orders,
        'total_spent': customer_orders.aggregate(Sum('price'))['price__sum'] or 0
    }
    return render(request, 'customer_detail.html', context)

@login_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.warning(request, "تم حذف الزبون بنجاح")
    return redirect('customers_list')

# --- 4. الشؤون المالية ---
@login_required
def purchases_list(request):
    if request.method == "POST":
        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        order_id = request.POST.get('order_id')
        category = request.POST.get('category')
        supplier = request.POST.get('supplier')
        date = request.POST.get('date') or timezone.now().date()

        Purchase.objects.create(
            item_name=item_name,
            price=price if price else 0,
            order_id=order_id if order_id and order_id != "" else None,
            category=category,
            supplier=supplier,
            date=date,
            purchased_by=request.user
        )
        messages.success(request, "تم تسجيل عملية الشراء")
        return redirect('purchases_list')

    purchases = Purchase.objects.all().order_by('-date')
    orders = Order.objects.exclude(status='completed')
    total_spent = purchases.aggregate(Sum('price'))['price__sum'] or 0
    return render(request, 'purchases.html', {'purchases': purchases, 'orders': orders, 'total_spent': total_spent})

@login_required
def finance_summary(request):
    total_income = Order.objects.filter(status='completed').aggregate(Sum('price'))['price__sum'] or 0
    total_expenses = Purchase.objects.aggregate(Sum('price'))['price__sum'] or 0
    total_salaries = Employee.objects.filter(is_active=True).aggregate(Sum('salary'))['salary__sum'] or 0
    
    grand_total_expenses = total_expenses + total_salaries
    net_profit = total_income - grand_total_expenses

    recent_purchases = Purchase.objects.all().order_by('-date')[:10]
    
    context = {
        'purchases': recent_purchases, 
        'total_income': total_income,
        'total_expenses': grand_total_expenses,
        'net_profit': net_profit,
        'total_salaries': total_salaries
    }
    return render(request, 'finance.html', context)

# --- 5. الموارد البشرية ---
@login_required
def hr_management(request):
    if request.method == "POST":
        name = request.POST.get('name')
        national_id = request.POST.get('national_id')
        email = request.POST.get('email')
        position = request.POST.get('job_title') 
        salary = request.POST.get('salary') or 0
        phone = request.POST.get('phone')
        joined_at = request.POST.get('hire_date') or timezone.now().date()
        is_active = request.POST.get('is_active') == 'on'
        
        Employee.objects.create(
            name=name, national_id=national_id, email=email, position=position,
            salary=salary, phone=phone, joined_at=joined_at, is_active=is_active
        )
        messages.success(request, "تم إضافة الموظف بنجاح")
        return redirect('hr_management')

    employees = Employee.objects.all().order_by('name')
    total_salaries = employees.filter(is_active=True).aggregate(Sum('salary'))['salary__sum'] or 0
    return render(request, 'employees.html', {'employees': employees, 'total_salaries': total_salaries})

@login_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.name = request.POST.get('name')
        employee.national_id = request.POST.get('national_id')
        employee.email = request.POST.get('email')
        employee.position = request.POST.get('job_title')
        employee.salary = request.POST.get('salary') or 0
        employee.phone = request.POST.get('phone')
        employee.joined_at = request.POST.get('hire_date') or employee.joined_at
        employee.is_active = request.POST.get('is_active') == 'on'
        employee.save()
        messages.success(request, "تم تحديث بيانات الموظف بنجاح")
    return redirect('hr_management')

# --- 6. الأرشيف الرقمي (تم تعديل الخطأ هنا) ---
@login_required
def digital_archive(request):
    if request.method == "POST":
        title = request.POST.get('title')
        # تم تعديل المفاتيح لتطابق الـ HTML والـ Model
        file_obj = request.FILES.get('document')  # كان 'file' والآن 'document'
        category = request.POST.get('category')  # كان 'file_type' والآن 'category'
        order_id = request.POST.get('order_id')
        
        # التأكد من عدم إرسال قيم فارغة للحقول المطلوبة (NOT NULL)
        if title and file_obj and category:
            DigitalArchive.objects.create(
                title=title, 
                file=file_obj, 
                file_type=category, # هنا نربط التصنيف بحقل نوع الملف
                order_id=order_id if order_id and order_id != "" else None
            )
            messages.success(request, "تمت أرشفة الملف بنجاح")
        else:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة واختيار ملف")
            
        return redirect('digital_archive')

    archives = DigitalArchive.objects.all().order_by('-uploaded_at')
    orders = Order.objects.filter(status='completed')
    return render(request, 'archive.html', {'archived_files': archives, 'orders': orders})

# --- 7. التقارير والإحصائيات ---
@login_required
def reports_view(request):
    order_stats = Order.objects.values('status').annotate(count=Count('id'))
    project_stats = Project.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'order_stats': order_stats,
        'project_stats': project_stats,
        'total_customers': Customer.objects.count(),
        'total_orders': Order.objects.count(),
    }
    return render(request, 'reports.html', context)
