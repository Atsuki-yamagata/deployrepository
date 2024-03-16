from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import TemplateView, View
from .forms import RegistForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import update_session_auth_hash
from .import forms
from django.contrib import messages
from django.core.exceptions import ValidationError

class HomeView(TemplateView):
    template_name = 'home.html'
    
class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(1200000)
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    pass


class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
@login_required
def change_password(request):
    password_change_form = forms.PasswordChangeForm(request.POST or None, instance=request.user)
    if password_change_form.is_valid():
        try:
            password_change_form.save()
            messages.success(request, 'パスワード更新完了しました。')
            update_session_auth_hash(request, request.user)
        except ValidationError as e:
            password_change_form.add_error('password', e)
    return render(
        request, 'accounts/change_password.html', context={
            'password_change_form': password_change_form, 
        }
    )
    
    