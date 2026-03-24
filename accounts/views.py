from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from .forms import LoginForm, UserRegisterForm, UserEditForm
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Bienvenido, {form.get_user().get_full_name() or form.get_user().username}.')
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserListView(View):
    def get(self, request):
        if not request.user.is_admin():
            messages.error(request, 'No tiene permisos para acceder a esta sección.')
            return redirect('dashboard')
        users = User.objects.all().order_by('username')
        return render(request, 'accounts/user_list.html', {'users': users})


@method_decorator(login_required, name='dispatch')
class UserCreateView(View):
    def get(self, request):
        if not request.user.is_admin():
            return redirect('dashboard')
        form = UserRegisterForm()
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Crear Usuario'})

    def post(self, request):
        if not request.user.is_admin():
            return redirect('dashboard')
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Crear Usuario'})


@method_decorator(login_required, name='dispatch')
class UserEditView(View):
    def get(self, request, pk):
        if not request.user.is_admin():
            return redirect('dashboard')
        user = get_object_or_404(User, pk=pk)
        form = UserEditForm(instance=user)
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Editar Usuario', 'object': user})

    def post(self, request, pk):
        if not request.user.is_admin():
            return redirect('dashboard')
        user = get_object_or_404(User, pk=pk)
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Editar Usuario', 'object': user})


@login_required
def user_delete(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario eliminado.')
        return redirect('user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'object': user})
