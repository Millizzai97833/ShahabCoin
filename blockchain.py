
import hashlib
import json
import time

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
    """Return the whole-SHC mining reward, capped by remaining supply."""
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


class Blockchain:
    def __init__(self):
        self.chain = [make_genesis_block()]

    def issued_supply(self):
        """Count mining rewards currently recorded in the chain."""
        total = 0
        for block in self.chain[1:]:
            for tx in block["transactions"]:
                if isinstance(tx, dict) and tx.get("type") == "mining_reward":
                    amount = tx.get("amount", 0)
                    if type(amount) is int and amount > 0:
                        total += amount
        return total

    def add_block(self, transactions, miner_address="miner-demo"):
        if not isinstance(transactions, list):
            raise ValueError("Transactions must be a list")

        if not isinstance(miner_address, str) or not miner_address.strip():
            raise ValueError("Miner address must be a non-empty string")

        for tx in transactions:
            if not isinstance(tx, dict):
                raise ValueError("Each transaction must be a dictionary")
            if tx.get("type") == "mining_reward":
                raise ValueError("Mining rewards are created by the blockchain")

        previous = self.chain[-1]
        height = len(self.chain)
        issued = self.issued_supply()
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
            "previous_hash": previous["hash"],
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
        return block

    def is_valid(self):
        issued = 0

        for index, block in enumerate(self.chain):
            if not isinstance(block, dict):
                return False

            content = {
                key: value
                for key, value in block.items()
                if key != "hash"
            }

            if block.get("hash") != hash_block(content):
                return False

            if index == 0:
                if block != make_genesis_block():
                    return False
                continue

            if block.get("index") != index:
                return False

            if block.get("previous_hash") != self.chain[index - 1].get("hash"):
                return False

            if not block["hash"].startswith("0" * DIFFICULTY):
                return False

            transactions = block.get("transactions")
            if not isinstance(transactions, list):
                return False

            expected_reward = reward_for_height(index, issued)
            reward_transactions = [
                tx for tx in transactions
                if isinstance(tx, dict)
                and tx.get("type") == "mining_reward"
            ]

            if expected_reward > 0:
                if not transactions or len(reward_transactions) != 1:
                    return False

                expected_tx = {
                    "type": "mining_reward",
                    "to": reward_transactions[0].get("to"),
                    "amount": expected_reward,
                    "currency": "SHC",
                }

                if reward_transactions[0] != expected_tx:
                    return False

                if not isinstance(expected_tx["to"], str) or not expected_tx["to"].strip():
                    return False

                issued += expected_reward
            elif reward_transactions:
                return False

            if issued > MAX_SUPPLY:
                return False

        return True
