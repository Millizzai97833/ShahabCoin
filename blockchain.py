
import hashlib
import json
import time

from wallet import verify_transaction

MAX_SUPPLY = 21_000_000
TARGET_BLOCK_SECONDS = 150
DIFFICULTY = 2
INITIAL_BLOCK_REWARD = 50
HALVING_INTERVAL = 210_000


def hash_block(block):
    data = json.dumps(
        block, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def reward_for_height(height, issued_before=0):
    """Return the whole-SHC mining reward within the supply limit."""
    if height < 1 or issued_before >= MAX_SUPPLY:
        return 0

    reward = INITIAL_BLOCK_REWARD >> ((height - 1) // HALVING_INTERVAL)
    return max(0, min(reward, MAX_SUPPLY - issued_before))


def make_genesis_block():
    block = {
        "index": 0,
        "timestamp": 0,
        "transactions": [],
        "previous_hash": "0" * 64,
        "nonce": 0,
    }
    block["hash"] = hash_block(block)
    return block


def _apply_transfer(transaction, balances, next_nonces):
    """Verify a signed transfer and apply it to temporary ledger state."""
    if not isinstance(transaction, dict):
        raise ValueError("Transaction must be a dictionary")

    required = {
        "from", "to", "amount", "nonce", "currency",
        "public_key", "signature",
    }
    if not required.issubset(transaction):
        raise ValueError("Missing signed transaction fields")

    if transaction.get("type") not in (None, "transfer"):
        raise ValueError("Unsupported transaction type")

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
        raise ValueError("Invalid nonce")

    public_hex = transaction["public_key"]
    signature = transaction["signature"]

    if not isinstance(public_hex, str):
        raise ValueError("Invalid public key")

    if not isinstance(signature, str) or not signature:
        raise ValueError("Invalid signature")

    try:
        public_bytes = bytes.fromhex(public_hex)
    except ValueError:
        raise ValueError("Invalid public key encoding") from None

    if hashlib.sha256(public_bytes).hexdigest() != sender:
        raise ValueError("Public key does not match sender")

    payload = {
        "from": sender,
        "to": recipient,
        "amount": amount,
        "nonce": nonce,
        "currency": "SHC",
    }

    if not verify_transaction(public_bytes, payload, signature):
        raise ValueError("Invalid transaction signature")

    expected_nonce = next_nonces.get(sender, 0)
    if nonce != expected_nonce:
        raise ValueError("Unexpected or replayed transaction nonce")

    if balances.get(sender, 0) < amount:
        raise ValueError("Insufficient SHC balance")

    balances[sender] -= amount
    balances[recipient] = balances.get(recipient, 0) + amount
    next_nonces[sender] = expected_nonce + 1


def _replay_and_validate(chain):
    """Validate every block and reconstruct its ledger state."""
    if not isinstance(chain, list) or not chain:
        raise ValueError("Blockchain is empty or malformed")

    balances = {}
    next_nonces = {}
    issued = 0

    for index, block in enumerate(chain):
        if not isinstance(block, dict):
            raise ValueError("Invalid block format")

        content = {
            key: value
            for key, value in block.items()
            if key != "hash"
        }

        if block.get("hash") != hash_block(content):
            raise ValueError("Block hash mismatch")

        if index == 0:
            if block != make_genesis_block():
                raise ValueError("Invalid genesis block")
            continue

        if block.get("index") != index:
            raise ValueError("Invalid block index")

        if block.get("previous_hash") != chain[index - 1].get("hash"):
            raise ValueError("Previous block hash mismatch")

        if not block["hash"].startswith("0" * DIFFICULTY):
            raise ValueError("Invalid proof of work")

        transactions = block.get("transactions")
        if not isinstance(transactions, list):
            raise ValueError("Invalid transaction list")

        expected_reward = reward_for_height(index, issued)

        reward_transactions = [
            tx for tx in transactions
            if isinstance(tx, dict)
            and tx.get("type") == "mining_reward"
        ]

        if expected_reward > 0:
            if not transactions or len(reward_transactions) != 1:
                raise ValueError("Missing or duplicate mining reward")

            reward_tx = transactions[0]

            if not isinstance(reward_tx, dict):
                raise ValueError("Invalid mining reward")

            miner = reward_tx.get("to")
            expected_tx = {
                "type": "mining_reward",
                "to": miner,
                "amount": expected_reward,
                "currency": "SHC",
            }

            if reward_tx != expected_tx:
                raise ValueError("Invalid mining reward")

            if not isinstance(miner, str) or not miner.strip():
                raise ValueError("Invalid miner address")

            issued += expected_reward
            balances[miner] = balances.get(miner, 0) + expected_reward
            user_transactions = transactions[1:]
        else:
            if reward_transactions:
                raise ValueError("Unexpected mining reward")
            user_transactions = transactions

        if issued > MAX_SUPPLY:
            raise ValueError("Maximum supply exceeded")

        for transaction in user_transactions:
            _apply_transfer(transaction, balances, next_nonces)

    return balances, next_nonces, issued


class Blockchain:
    def __init__(self):
        self.chain = [make_genesis_block()]

    def issued_supply(self):
        """Return the total valid mining rewards in the chain."""
        _balances, _nonces, issued = _replay_and_validate(self.chain)
        return issued

    def add_block(self, transactions, miner_address="miner-demo"):
        """Validate transactions, mine a block, and append it."""
        if not isinstance(transactions, list):
            raise ValueError("Transactions must be a list")

        if not isinstance(miner_address, str) or not miner_address.strip():
            raise ValueError("Miner address must be non-empty")

        balances, next_nonces, issued = _replay_and_validate(self.chain)

        # Validate transfers before mining. Work on copies so rejected
        # transactions cannot alter the existing chain's ledger state.
        pending_balances = dict(balances)
        pending_nonces = dict(next_nonces)

        for transaction in transactions:
            if (
                isinstance(transaction, dict)
                and transaction.get("type") == "mining_reward"
            ):
                raise ValueError("Mining rewards are created by the blockchain")

            _apply_transfer(
                transaction, pending_balances, pending_nonces
            )

        height = len(self.chain)
        reward = reward_for_height(height, issued)

        block_transactions = []

        if reward > 0:
            block_transactions.append({
                "type": "mining_reward",
                "to": miner_address,
                "amount": reward,
                "currency": "SHC",
            })

        block_transactions.extend(transactions)

        block = {
            "index": height,
            "timestamp": int(time.time()),
            "transactions": block_transactions,
            "previous_hash": self.chain[-1]["hash"],
            "nonce": 0,
        }

        target = "0" * DIFFICULTY

        while True:
            block_hash = hash_block(block)
            if block_hash.startswith(target):
                block["hash"] = block_hash
                break
            block["nonce"] += 1

        self.chain.append(block)

        # Ensure the resulting chain can be fully replayed and validated.
        try:
            _replay_and_validate(self.chain)
        except Exception:
            self.chain.pop()
            raise

        return block

    def is_valid(self):
        try:
            _replay_and_validate(self.chain)
            return True
        except (ValueError, TypeError, KeyError, IndexError, OverflowError):
            return False
        
