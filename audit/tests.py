from django.test import TestCase
from accounts.models import User
from .models import AuditEvent
from .services import record_event, verify_chain

class AuditTrailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="auditor-test", password="Strong-Test-Password-1")

    def test_hash_chain_verifies_after_events(self):
        record_event(actor=self.user, action="test_one", outcome="success")
        record_event(actor=self.user, action="test_two", outcome="denied")
        self.assertTrue(verify_chain())

    def test_audit_event_cannot_be_updated_through_model(self):
        event = record_event(actor=self.user, action="test", outcome="success")
        event.action = "changed"
        with self.assertRaises(RuntimeError):
            event.save()

    def test_audit_event_cannot_be_deleted_through_model(self):
        event = record_event(actor=self.user, action="test", outcome="success")
        with self.assertRaises(RuntimeError):
            event.delete()

    def test_tampered_event_breaks_chain_verification(self):
        record_event(actor=self.user, action="test", outcome="success")
        event = AuditEvent.objects.first()
        # Simulate a privileged direct database update, bypassing model.save().
        AuditEvent.objects.filter(pk=event.pk).update(outcome="tampered")
        self.assertFalse(verify_chain())
