from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f'Merci {username}, votre compte a été créé avec succés, vous pouvez maintenant vous connecter'
                )
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'management/register.html', {'form': form})


@login_required
def profile(request):

    user_pk = request.user.pk
    user_profile = Profile.objects.get(user_id=user_pk)

    context = {
        "title": "Mon Profil",
    }
    return render(request, 'user/profile.html', context)
