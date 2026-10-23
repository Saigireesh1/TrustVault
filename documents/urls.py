from django.urls import path
from . import views
app_name = "documents"
urlpatterns = [
    path("", views.document_list, name="list"),
    path("documents/<uuid:pk>/", views.document_detail, name="detail"),
    path("documents/<uuid:pk>/download/", views.document_download, name="download"),
    path("documents/<uuid:pk>/edit/", views.document_edit, name="edit"),
    path("documents/<uuid:pk>/delete/", views.document_delete, name="delete"),
    path("documents/<uuid:pk>/grants/", views.grant_access, name="grant"),
    path("documents/<uuid:pk>/grants/<int:user_id>/revoke/", views.revoke_access, name="revoke"),
]
