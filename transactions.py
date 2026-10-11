import hashlib
from wallet import verify_transaction


class TransactionLedger:
    """Educational in-memory ledger for ShahabCoin transactions."""

    def __init__(self, initial_balances=None):
        self.balances = dict(initial_balances or {})
        self.transactions = []
        self.used_nonces = set()

    def apply(self, transaction, public_key_bytes, signature):
        required = {"from", "to", "amount", "nonce", "currency"}

        if not isinstance(transaction, dict):
            return False, "Invalid transaction format"

        if not required.issubset(transaction):
            return False, "Missing transaction fields"

        sender = transaction["from"]
        recipient = transaction["to"]
        amount = transaction["amount"]
        nonce = transaction["nonce"]

        if transaction["currency"] != "SHC":
            return False, "Unsupported currency"

        if not isinstance(sender, str) or not sender:
            return False, "Invalid sender"

        if not isinstance(recipient, str) or not recipient:
            return False, "Invalid recipient"

        if type(amount) is not int or amount <= 0:
            return False, "Amount must be a positive integer"

        if type(nonce) is not int or nonce < 0:
            return False, "Nonce must be a non-negative integer"

        if not isinstance(public_key_bytes, bytes):
            return False, "Invalid public key"

        if hashlib.sha256(public_key_bytes).hexdigest() != sender:
            return False, "Public key does not match sender"

        if not verify_transaction(
            public_key_bytes, transaction, signature
        ):
            return False, "Invalid transaction signature"

        if (sender, nonce) in self.used_nonces:
            return False, "Transaction nonce already used"

        if self.balances.get(sender, 0) < amount:
            return False, "Insufficient test balance"

        self.balances[sender] -= amount
        self.balances[recipient] = (
            self.balances.get(recipient, 0) + amount
        )

        self.used_nonces.add((sender, nonce))
        self.transactions.append(dict(transaction))

        return True, "Test transaction accepted"
