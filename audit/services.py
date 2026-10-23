import hashlib
import json
from django.db import transaction
from django.utils import timezone
from .models import AuditChainState, AuditEvent

GENESIS = "0" * 64

def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)

def record_event(*, actor, action, outcome, document=None, details=None, request_id=""):
    """Append an event to a serialized hash chain inside a DB transaction.

    This detects ordinary record edits/deletions when verifying the chain. It is
    NOT a substitute for independently protected external audit storage.
    """
    with transaction.atomic():
        state, _ = AuditChainState.objects.get_or_create(id=1, defaults={"last_hash": GENESIS, "sequence": 0})
        state = AuditChainState.objects.select_for_update().get(pk=1)
        seq = state.sequence + 1
        event_time = timezone.now()
        timestamp = event_time.isoformat()
        doc_id = str(document.pk) if document else ""
        actor_id = actor.pk if actor is not None and getattr(actor, "is_authenticated", False) else None
        actor_id_snapshot = str(actor_id) if actor_id is not None else ""
        actor_label = getattr(actor, "username", "anonymous") if actor_id else "anonymous"
        safe_details = details or {}
        payload = {"sequence": seq, "actor_id_snapshot": actor_id_snapshot, "actor_label": actor_label,
                   "action": action, "document_id_text": doc_id, "outcome": outcome,
                   "details": safe_details, "request_id": request_id,
                   "timestamp": timestamp, "previous_hash": state.last_hash}
        digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
        event = AuditEvent.objects.create(
            actor=actor if actor_id else None, actor_label=actor_label, actor_id_snapshot=actor_id_snapshot, action=action,
            document_id_text=doc_id, outcome=outcome, details=safe_details,
            request_id=request_id, sequence=seq, previous_hash=state.last_hash,
            event_hash=digest, timestamp=event_time)
        state.sequence = seq
        state.last_hash = digest
        state.save(update_fields=["sequence", "last_hash"])
        return event

def verify_chain():
    previous = GENESIS
    expected_sequence = 1
    for event in AuditEvent.objects.order_by("sequence"):
        payload = {"sequence": event.sequence, "actor_id_snapshot": event.actor_id_snapshot,
                   "actor_label": event.actor_label, "action": event.action,
                   "document_id_text": event.document_id_text, "outcome": event.outcome,
                   "details": event.details, "request_id": event.request_id,
                   "timestamp": event.timestamp.isoformat(), "previous_hash": event.previous_hash}
        digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
        if event.sequence != expected_sequence or event.previous_hash != previous or event.event_hash != digest:
            return False
        previous = event.event_hash
        expected_sequence += 1
    return True
