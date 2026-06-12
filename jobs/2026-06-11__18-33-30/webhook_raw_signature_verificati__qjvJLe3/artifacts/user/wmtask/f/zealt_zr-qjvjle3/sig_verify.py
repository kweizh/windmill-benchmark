import hmac
import hashlib
import wmill


def main(raw_string: str, x_signature: str) -> dict:
    secret = wmill.get_variable("f/zealt_zr-qjvjle3/webhook_secret")
    computed = hmac.new(
        secret.encode("utf-8"),
        raw_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if hmac.compare_digest(computed, x_signature):
        return {"valid": True}
    return {"valid": False}