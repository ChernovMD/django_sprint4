# users/views.py
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from blog.models import Post
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import UserChangeForm

User = get_user_model()


def registration_view(request):
    return render(request, "registration/register.html")


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user == profile:
        # Автор видит все свои посты
        posts = Post.objects.filter(author=profile).order_by("-pub_date")
    else:
        # Остальные — только опубликованные
        posts = Post.objects.filter(
            author=profile,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        ).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "users/profile.html",
        {"profile": profile, "page_obj": page_obj}
    )


@login_required
def profile_edit_view(request, username):
    if request.user.username != username:
        return redirect("users:profile", username=request.user.username)

    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:profile", username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})
