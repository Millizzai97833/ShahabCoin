
import hashlib
import secrets


def generate_demo_key():
    """
    Generate a random 32-byte secret for local experimentation.
    This is not yet a production wallet implementation.
    """
    return secrets.token_bytes(32)


def demo_address(public_key_bytes):
    """
    Create a deterministic demo identifier from public-key bytes.
    This is NOT a complete cryptocurrency address format.
    """
    return hashlib.sha256(public_key_bytes).hexdigest()


if __name__ == "__main__":
    secret = generate_demo_key()

    print("Generated a demo secret key.")
    print("Do not share or publish secret keys.")
    print("No address generated: a public-key derivation scheme")
    print("and signature implementation are required first.")
