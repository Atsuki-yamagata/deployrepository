from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView,
    FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
from . import forms
from .models import CustInfo
from accounts.models import Users
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from datetime import datetime
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from .forms import CustUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.db.models import Count



# Create your views here.

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True
    
    def test_user_func(self):
        Users = get_object_or_404(Users, pk=self.kwargs['pk'])
        return self.get_queryset().filter(user_id=self.request.user.id).exists()

    def test_cust_func(self):
        CustInfo = get_object_or_404(CustInfo, pk=self.kwargs['pk'])
        return self.get_queryset().filter(user_id=self.request.user.id).exists()
    
    def test_func(self):
        if self.test_user_func() or self.test_cust_func():
            return True
        else:
            raise PermissionDenied
    
class UserListView(LoginRequiredMixin, ListView, OnlyYouMixin):
    model = Users
    template_name = os.path.join('custmanage', 'user_info.html')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(id=self.request.user.id).order_by('id')

class CustomerListView(LoginRequiredMixin, ListView):
    model = CustInfo
    template_name = os.path.join('custmanage', 'cust_list.html')
    
        # 絞り込み
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.user.id  # ログインユーザーのIDを取得
        queryset = queryset.filter(user_id=user_id)  # ユーザーIDでフィルタリング
        Company_name = self.request.GET.get('Company_name', None)
        Cust_job_name = self.request.GET.get('Cust_job_name', None)
        Cust_skill_name = self.request.GET.get('Cust_skill_name', None)
        if Company_name:
            queryset = queryset.filter( Company=Company_name )
        if Cust_job_name:
            queryset = queryset.filter( Cust_job=Cust_job_name )  
        if Cust_skill_name:
            queryset = queryset.filter( Cust_skill=Cust_skill_name )
        order_by_importance_level = self.request.GET.get('order_by_importance_level', None)
        if order_by_importance_level == '1':
            queryset = queryset.order_by('importance_level')
        elif order_by_importance_level == '2':
            queryset = queryset.order_by('-importance_level')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        cust_info_user = CustInfo.objects.filter(user_id=user_id).values('Company', 'Cust_job', 'Cust_skill').annotate(Count('id'))
        user_filter = CustInfo.objects.filter(user_id=user_id).values_list('Company', flat=True).distinct()
        unique_companies = CustInfo.objects.filter(user_id=user_id).values_list('Company', flat=True).distinct()
        unique_jobs = CustInfo.objects.filter(user_id=user_id).values_list('Cust_job', flat=True).distinct()
        unique_skills = CustInfo.objects.filter(user_id=user_id).values_list('Cust_skill', flat=True).distinct()
        context['cust_info_user'] = CustInfo.objects.filter(user_id=self.request.user.id)        
        context['Company'] = self.request.GET.get('Company', '')
        context['Cust_job'] = self.request.GET.get('Cust_job', '')
        context['Cust_skill'] = self.request.GET.get('Cust_skill', '')
        context['selected_company'] = self.request.GET.get('Company_name', '')
        context['unique_companies'] = unique_companies
        context['unique_jobs'] = unique_jobs
        context['unique_skills'] = unique_skills
        order_by_importance_level = self.request.GET.get('order_by_importance_level', 0)
        if order_by_importance_level == '1':
            context['ascending'] = True
        elif order_by_importance_level == '2':
            context['descending'] = True
        return context

class CustCreateView(CreateView, OnlyYouMixin, LoginRequiredMixin):
    model = CustInfo
    fields = ['Cust_name', 'Company', 'Company_address', 'Cust_post', 'Cust_job', 'Cust_skill',
              'Cust_mail', 'Cust_phone_num', 'importance_level', 'memo']
    template_name = os.path.join( 'custmanage', 'add_cust_info.html')
    success_url = reverse_lazy('custmanage:cust_list')


    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.instance.create_at = datetime.now()
        form.instance.update_at = datetime.now()
        return super(CustCreateView, self).form_valid(form)
        
class CustDetailView(LoginRequiredMixin, DetailView, OnlyYouMixin):
    model = CustInfo
    template_name = os.path.join('custmanage', 'cust_detail.html')
              
class CustDeleteView(LoginRequiredMixin, DeleteView, OnlyYouMixin):
    model  = CustInfo
    template_name = os.path.join('custmanage','delete_info.html')
    success_url = reverse_lazy('custmanage:cust_list')
    extra_context = {'style': 'padding-left: 20px;'}

class UserDeleteView(LoginRequiredMixin, DeleteView, OnlyYouMixin):
    model  = Users
    template_name = os.path.join('custmanage','delete_user.html')
    extra_context = {'style': 'padding-left: 20px;'}

    
    def get_success_url(self):
        return reverse_lazy('accounts:user_login')

    
class CustUpdateView(LoginRequiredMixin, UpdateView, OnlyYouMixin):
    model = CustInfo
    template_name = os.path.join('custmanage', 'update_cust_info.html')
    extra_context = {'style': 'padding-left: 20px;'}

class UserUpdateView(UpdateView, OnlyYouMixin):
    model = Users
    form_class = UserUpdateForm
    template_name = 'custmanage/edit_user_info.html'
    extra_context = {'style': 'padding-left: 20px;'}

    
    def get_success_url(self):
        return reverse_lazy('custmanage:user_info', kwargs={'pk': self.object.pk})
    
class CustUpdateView(UpdateView, OnlyYouMixin, LoginRequiredMixin):
    model = CustInfo
    form_class = CustUpdateForm
    template_name = 'custmanage/edit_cust_info.html'
    
    def get_success_url(self):
        return reverse_lazy('custmanage:cust_detail', kwargs={'pk': self.object.pk})
    
def server_error(request):
    return render(request, 'accounts/500.html', status=500)