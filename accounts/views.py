
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST

from .forms import RegistrationForm


def can_approve_users(user):
    """Only active owners, admins, and superusers can approve users."""
    return (
        user.is_authenticated
        and user.is_active
        and (
            user.is_superuser
            or user.role in ("ADMIN", "OWNER")
        )
    )


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your account was created. Please wait for an administrator "
                "to approve it before signing in.",
            )
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@user_passes_test(can_approve_users)
def pending_user_approvals(request):
    User = get_user_model()

    pending_users = User.objects.filter(
        is_active=False,
        role=User.Role.VIEWER,
    ).order_by("date_joined")

    return render(
        request,
        "accounts/pending_approvals.html",
        {"pending_users": pending_users},
    )


@require_POST
@user_passes_test(can_approve_users)
def approve_user(request, user_id):
    User = get_user_model()

    pending_user = get_object_or_404(
        User,
        pk=user_id,
        is_active=False,
        role=User.Role.VIEWER,
    )

    pending_user.is_active = True
    pending_user.save(update_fields=["is_active"])

    messages.success(
        request,
        f"Account '{pending_user.username}' has been approved.",
    )

    return redirect("pending_user_approvals")
