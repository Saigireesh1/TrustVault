
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from .models import AuditEvent
from .services import verify_chain


def can_view_audit(user):
    return (
        user.is_authenticated
        and user.is_active
        and (
            user.is_superuser
            or user.role in ("ADMIN", "OWNER")
        )
    )


@login_required
@user_passes_test(can_view_audit)
def dashboard(request):
    events = AuditEvent.objects.select_related("actor").all()[:250]

    return render(
        request,
        "audit/dashboard.html",
        {
            "events": events,
            "chain_valid": verify_chain(),
        },
    )
