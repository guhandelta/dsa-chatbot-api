"""Administrative actions share the transaction with the change they describe."""
import json
from fastapi.encoders import jsonable_encoder
from app.db.models import AdminAuditEvent


def record(session, actor_id, action, target_id, *, reason='', before=None, after=None):
    session.add(AdminAuditEvent(actor_id=actor_id, action=action, target_id=target_id,
        reason=reason, before_json=json.dumps(jsonable_encoder(before or {})),
        after_json=json.dumps(jsonable_encoder(after or {}))))
