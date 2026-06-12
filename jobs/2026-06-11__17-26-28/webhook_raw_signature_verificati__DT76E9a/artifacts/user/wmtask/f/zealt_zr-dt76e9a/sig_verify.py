import hmac
import hashlib
import wmill
from typing import Optional

def main(raw_string: Optional[str] = None, x_signature: Optional[str] = None):
    if raw_string is None or x_signature is None:
        return {"valid": False, "error": "Missing raw_string or x_signature"}
    
    try:
        # Get the secret variable path
        secret = wmill.get_variable("f/zealt_zr-dt76e9a/webhook_secret")
        
        # Compute HMAC-SHA256 hex digest of raw_string
        computed = hmac.new(
            secret.encode("utf-8"),
            raw_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        # Compare in a timing-safe manner
        if hmac.compare_digest(computed, x_signature):
            return {"valid": True}
        else:
            return {"valid": False, "error": "Signature mismatch"}
    except Exception as e:
        return {"valid": False, "error": str(e)}
