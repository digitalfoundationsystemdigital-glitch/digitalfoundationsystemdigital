# Digital Foundation System

منظومة Django لإدارة المؤسسة الرقمية: لوحة تحكم، مشاريع، طلبات، زبائن، مشتريات، مالية، موارد بشرية، وأرشيف رقمي.

## التشغيل المحلي

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

ثم افتح:

```text
http://127.0.0.1:8000/
```

صفحة الدخول الخاصة بالمنظومة:

```text
http://127.0.0.1:8000/login/
```

## ملاحظات

- قاعدة البيانات المحلية `db.sqlite3` غير مرفوعة إلى GitHub.
- مجلدات الملفات المرفوعة `media` والبيئة الافتراضية `venv` غير مرفوعة.
- بعد تنزيل المشروع على جهاز جديد، شغّل `migrate` وأنشئ مستخدمًا جديدًا بالأمر `createsuperuser`.

