import wmill
import hmac
import hashlib
from typing import Any

def main(x_signature: str, body: Any):
    secret = wmill.get_variable("f/zealt_zr-x7uusvv/webhook_secret")
    
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    elif isinstance(body, bytes):
        body_bytes = body
    else:
        body_bytes = str(body).encode('utf-8')
        
    computed_hmac = hmac.new(
        secret.encode('utf-8'),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    if hmac.compare_digest(computed_hmac, x_signature):
        return {"valid": True}
    else:
        return {"valid": False}
