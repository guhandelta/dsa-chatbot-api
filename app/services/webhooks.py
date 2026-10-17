"""Stripe v1 signatures over the raw body, with bounded replay tolerance."""
import hashlib
import hmac
import json
import time
from fastapi import HTTPException


def verified_event(raw:bytes,header:str,secret:str):
    if not secret:raise HTTPException(503,'Stripe webhook secret is not configured.')
    try:
        parts=[part.split('=',1) for part in header.split(',')]
        stamp=int(next(value for key,value in parts if key=='t'))
        signatures=[value for key,value in parts if key=='v1']
        if abs(time.time()-stamp)>300:raise ValueError('Expired signature')
        expected=hmac.new(secret.encode(),str(stamp).encode()+b'.'+raw,hashlib.sha256).hexdigest()
        if not any(hmac.compare_digest(expected,sig) for sig in signatures):raise ValueError('Invalid signature')
        event=json.loads(raw)
        if not isinstance(event,dict) or not isinstance(event.get('id'),str) or not event['id'] or len(event['id'])>255:raise ValueError('Missing event ID')
        return event
    except (ValueError,StopIteration,TypeError):
        raise HTTPException(400,'Invalid or expired Stripe signature / payload.')
