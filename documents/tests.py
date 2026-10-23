
from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from .models import Document, DocumentGrant
from .permissions import can_read, can_edit
from audit.models import AuditEvent


class DocumentAuthorizationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="Strong-Test-Password-1",
            role=User.Role.OWNER,
        )
        self.viewer = User.objects.create_user(
            username="viewer",
            password="Strong-Test-Password-2",
            role=User.Role.VIEWER,
        )
        self.other = User.objects.create_user(
            username="other",
            password="Strong-Test-Password-3",
            role=User.Role.VIEWER,
        )

        self.doc = Document.objects.create(
            owner=self.owner,
            title="Secret contract",
            category="Legal",
            original_filename="secret.txt",
            storage_key="nonexistent-key.txt",
            content_type="text/plain",
            size_bytes=6,
            sha256="a" * 64,
        )

    def test_ungranted_user_cannot_read(self):
        self.assertFalse(can_read(self.other, self.doc))

    def test_owner_can_read_and_edit(self):
        self.assertTrue(can_read(self.owner, self.doc))
        self.assertTrue(can_edit(self.owner, self.doc))

    def test_read_grant_does_not_allow_edit(self):
        DocumentGrant.objects.create(
            document=self.doc,
            user=self.viewer,
            permission="read",
            granted_by=self.owner,
        )
        self.assertTrue(can_read(self.viewer, self.doc))
        self.assertFalse(can_edit(self.viewer, self.doc))

    def test_edit_grant_allows_read_and_edit(self):
        DocumentGrant.objects.create(
            document=self.doc,
            user=self.viewer,
            permission="edit",
            granted_by=self.owner,
        )
        self.assertTrue(can_read(self.viewer, self.doc))
        self.assertTrue(can_edit(self.viewer, self.doc))

    def test_download_endpoint_denies_ungranted_user_and_audits(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("documents:download", args=[self.doc.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            AuditEvent.objects.filter(
                action="download",
                outcome="denied",
                actor=self.other,
            ).exists()
        )

    def test_revoke_is_immediate_for_next_request(self):
        DocumentGrant.objects.create(
            document=self.doc,
            user=self.viewer,
            permission="read",
            granted_by=self.owner,
        )
        self.client.force_login(self.viewer)

        detail = self.client.get(
            reverse("documents:detail", args=[self.doc.pk])
        )
        self.assertEqual(detail.status_code, 200)

        DocumentGrant.objects.filter(
            document=self.doc,
            user=self.viewer,
        ).delete()

        response = self.client.post(
            reverse("documents:download", args=[self.doc.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_viewer_cannot_grant_access(self):
        self.client.force_login(self.viewer)
        response = self.client.post(
            reverse("documents:grant", args=[self.doc.pk]),
            {"user": self.other.pk, "permission": "read"},
        )
        self.assertEqual(response.status_code, 403)

    def test_search_does_not_return_ungranted_document(self):
        self.client.force_login(self.other)

        response = self.client.get(
            reverse("documents:list"),
            {"q": "Secret contract"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            response.context["documents"]
            .filter(pk=self.doc.pk)
            .exists()
        )

    def test_ungranted_user_cannot_edit_document(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("documents:edit", args=[self.doc.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_ungranted_user_cannot_delete_document(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("documents:delete", args=[self.doc.pk])
        )
        self.assertEqual(response.status_code, 403)

        self.doc.refresh_from_db()
        self.assertIsNone(self.doc.deleted_at)

    def test_grant_revocation_endpoint_is_owner_only(self):
        DocumentGrant.objects.create(
            document=self.doc,
            user=self.viewer,
            permission="read",
            granted_by=self.owner,
        )
        self.client.force_login(self.other)

        response = self.client.post(
            reverse(
                "documents:revoke",
                args=[self.doc.pk, self.viewer.pk],
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            DocumentGrant.objects.filter(
                document=self.doc,
                user=self.viewer,
            ).exists()
        )
