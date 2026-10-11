
import hashlib

from wallet import sign_transaction, verify_transaction


def _payload(transaction):
    """Fields covered by the wallet's digital signature."""
    return {
        "from": transaction["from"],
        "to": transaction["to"],
        "amount": transaction["amount"],
        "nonce": transaction["nonce"],
        "currency": transaction["currency"],
    }


def _validate_transfer(transaction, balances, next_nonces):
    """Validate and apply one transfer to the supplied ledger state."""
    if not isinstance(transaction, dict):
        raise ValueError("Invalid transaction format")

    required = {
        "from", "to", "amount", "nonce", "currency",
        "public_key", "signature",
    }
    if not required.issubset(transaction):
        raise ValueError("Missing transaction fields")

    sender = transaction["from"]
    recipient = transaction["to"]
    amount = transaction["amount"]
    nonce = transaction["nonce"]

    if not isinstance(sender, str) or not sender:
        raise ValueError("Invalid sender")

    if not isinstance(recipient, str) or not recipient:
        raise ValueError("Invalid recipient")

    if sender == recipient:
        raise ValueError("Sender and recipient must differ")

    if transaction["currency"] != "SHC":
        raise ValueError("Unsupported currency")

    if type(amount) is not int or amount <= 0:
        raise ValueError("Amount must be a positive integer")

    if type(nonce) is not int or nonce < 0:
        raise ValueError("Nonce must be a non-negative integer")

    public_hex = transaction["public_key"]
    signature = transaction["signature"]

    if not isinstance(public_hex, str):
        raise ValueError("Invalid public key")

    try:
        public_bytes = bytes.fromhex(public_hex)
    except ValueError:
        raise ValueError("Invalid public key encoding") from None

    if hashlib.sha256(public_bytes).hexdigest() != sender:
        raise ValueError("Public key does not match sender")

    payload = _payload(transaction)

    if not verify_transaction(public_bytes, payload, signature):
        raise ValueError("Invalid transaction signature")

    expected_nonce = next_nonces.get(sender, 0)
    if nonce != expected_nonce:
        raise ValueError("Unexpected nonce or replayed transaction")

    if balances.get(sender, 0) < amount:
        raise ValueError("Insufficient SHC balance")

    balances[sender] -= amount
    balances[recipient] = balances.get(recipient, 0) + amount
    next_nonces[sender] = expected_nonce + 1


def calculate_balances(blockchain):
    """Reconstruct balances by replaying the validated local chain."""
    if not blockchain.is_valid():
        raise ValueError("Blockchain validation failed")

    balances = {}
    next_nonces = {}

    for block in blockchain.chain[1:]:
        for transaction in block["transactions"]:
            if transaction.get("type") == "mining_reward":
                address = transaction["to"]
                amount = transaction["amount"]
                balances[address] = balances.get(address, 0) + amount
            else:
                _validate_transfer(
                    transaction, balances, next_nonces
                )

    return balances


def get_next_nonce(blockchain, address):
    """Return the next transaction nonce for an address."""
    calculate_balances(blockchain)

    next_nonce = 0

    for block in blockchain.chain[1:]:
        for transaction in block["transactions"]:
            if (
                transaction.get("type") != "mining_reward"
                and transaction.get("from") == address
            ):
                next_nonce += 1

    return next_nonce


def create_signed_transfer(
    private_key, public_key_bytes, recipient, amount, nonce
):
    """Create a signed transfer; does not broadcast or mine it."""
    sender = hashlib.sha256(public_key_bytes).hexdigest()

    payload = {
        "from": sender,
        "to": recipient,
        "amount": amount,
        "nonce": nonce,
        "currency": "SHC",
    }

    signature = sign_transaction(private_key, payload)

    return {
        **payload,
        "public_key": public_key_bytes.hex(),
        "signature": signature,
    }


def apply_transfer_block(blockchain, transaction, miner_address):
    """Validate a transfer, then record it in a newly mined block."""
    balances = calculate_balances(blockchain)

    # Validate against the current ledger before mining.
    next_nonces = {}

    for block in blockchain.chain[1:]:
        for tx in block["transactions"]:
            if tx.get("type") != "mining_reward":
                sender = tx["from"]
                next_nonces[sender] = next_nonces.get(sender, 0) + 1

    _validate_transfer(transaction, balances, next_nonces)

    block = blockchain.add_block(
        [transaction],
        miner_address=miner_address,
    )

    # Check that the resulting chain and transfer history are valid.
    calculate_balances(blockchain)
    return block
  
