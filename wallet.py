
import base64
import hashlib
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


def create_wallet():
    """Create an Ed25519 key pair for local testing."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    address = hashlib.sha256(public_bytes).hexdigest()

    return private_key, public_bytes, private_bytes, address


def sign_transaction(private_key, transaction):
    """Sign canonical transaction JSON."""
    message = json.dumps(
        transaction, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    signature = private_key.sign(message)
    return base64.b64encode(signature).decode("ascii")


def verify_transaction(public_key_bytes, transaction, signature):
    """Return False if a signature is invalid."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PublicKey,
    )

    message = json.dumps(
        transaction, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    try:
        public_key = Ed25519PublicKey.from_public_bytes(
            public_key_bytes
        )
        public_key.verify(base64.b64decode(signature), message)
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


if __name__ == "__main__":
    private_key, public_bytes, private_bytes, address = create_wallet()

    transaction = {
        "from": address,
        "to": "demo-recipient",
        "amount": 1,
        "currency": "SHC",
        "network": "ShahabCoin-test",
    }

    signature = sign_transaction(private_key, transaction)

    print("Demo wallet created successfully.")
    print("Address:", address)
    print("Signature valid:", verify_transaction(
        public_bytes, transaction, signature
    ))
    print("This is a local test; no SHC was transferred.")
    print("Private key intentionally not displayed.")
