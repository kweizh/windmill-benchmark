import hmac
import hashlib
import wmill


def main(raw_string: str, x_signature: str = ""):
    """Verify HMAC-SHA256 signature of the raw request body.

    Args:
        raw_string: The raw request body (provided by Windmill when raw=true query arg is used)
        x_signature: The signature from the X-Signature header (provided by Windmill
                     when include_header=X-Signature query arg is used)
    """
    secret = wmill.get_variable("f/zealt_zr-ye8nhqc/webhook_secret")

    if not x_signature:
        return {"valid": False, "wm_status_code": 401}

    computed = hmac.new(
        secret.encode("utf-8"),
        raw_string.encode("utf-8") if raw_string else b"",
        hashlib.sha256,
    ).hexdigest()

    valid = hmac.compare_digest(computed, x_signature)

    if valid:
        return {"valid": True}
    else:
        return {"valid": False, "wm_status_code": 401}
