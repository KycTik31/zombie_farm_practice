from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm, EditProfileForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            return redirect('channel', username=user.username)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "edit_profile.html", {"form": form})
