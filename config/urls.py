
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from accounts.views import (
    register,
    pending_user_approvals,
    approve_user,
)

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),

    # Login and logout
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # Account registration
    path(
        "accounts/register/",
        register,
        name="register",
    ),

    # Owner/admin user approval
    path(
        "accounts/pending-approvals/",
        pending_user_approvals,
        name="pending_user_approvals",
    ),
    path(
        "accounts/approve/<int:user_id>/",
        approve_user,
        name="approve_user",
    ),

    # Documents
    path("", include("documents.urls")),

    # Audit trail
    path("audit/", include("audit.urls")),
]
