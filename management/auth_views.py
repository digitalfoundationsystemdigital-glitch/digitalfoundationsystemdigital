from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View


class AuthPortalView(View):
    def get(self, request):
        return render(request, "auth_portal.html")


class EmployeeLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True


class AdminLoginView(LoginView):
    template_name = "admin_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("admin:index")

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser:
            form.add_error(None, "هذه الواجهة مخصصة لمدير النظام فقط.")
            messages.error(self.request, "هذه الواجهة مخصصة لمدير النظام فقط.")
            return self.form_invalid(form)

        auth_login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())
