import hmac
import hashlib
import wmill


def main(raw_string: str = "", x_signature: str = "") -> dict:
    """
    Verify an HMAC-SHA256 webhook signature.

    Windmill forwards:
      - raw_string : the verbatim request body  (via ?raw=true)
      - x_signature: the X-Signature header     (via ?include_header=X-Signature)

    The signing secret is read from the Windmill Variable at
    f/zealt_zr-ipf5jne/webhook_secret (stored as a secret variable).
    """
    secret: str = wmill.get_variable("f/zealt_zr-ipf5jne/webhook_secret")

    expected_mac = hmac.new(
        secret.encode("utf-8"),
        raw_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if hmac.compare_digest(expected_mac, x_signature.lower()):
        return {"valid": True}

    return {"valid": False}
