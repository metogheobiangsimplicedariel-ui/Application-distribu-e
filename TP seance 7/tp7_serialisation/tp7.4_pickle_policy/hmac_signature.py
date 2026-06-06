import hmac
import hashlib
import json

SECRET_KEY = b"ma_cle_secrete_partagee"


def sign_payload(data: dict) -> tuple:
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
    sig = hmac.new(SECRET_KEY, payload.encode("utf-8"), hashlib.sha256)
    return payload, sig.hexdigest()


def verify_payload(payload_json: str, received_sig: str) -> bool:
    expected = hmac.new(SECRET_KEY, payload_json.encode("utf-8"), hashlib.sha256)
    return hmac.compare_digest(expected.hexdigest(), received_sig)
