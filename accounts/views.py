from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AccountCreateForm


def register(request):
    if request.method == 'POST':
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if request.user.is_authenticated and request.user.is_admin():
                user.role = form.cleaned_data.get('role', 'intern')
            else:
                user.role = 'intern'
            user.email = form.cleaned_data.get('email', '')
            user.save()
            messages.success(request, 'Account created. You can now log in.')
            return redirect('accounts:login')
    else:
        form = AccountCreateForm()
        if not (request.user.is_authenticated and request.user.is_admin()):
            form.fields.pop('role', None)

    return render(request, 'accounts/register.html', {'form': form})
