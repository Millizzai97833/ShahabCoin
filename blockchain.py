
import hashlib
import json
import time

MAX_SUPPLY = 21_000_000
TARGET_BLOCK_SECONDS = 150

# Educational difficulty: each block hash must start with two zeros.
DIFFICULTY = 2


def hash_block(block):
    data = json.dumps(
        block, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


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

    def add_block(self, transactions):
        previous = self.chain[-1]
        block = {
            "index": len(self.chain),
            "timestamp": int(time.time()),
            "transactions": transactions,
            "previous_hash": previous["hash"],
            "nonce": 0,
        }

        # Proof of Work: search for a hash with the required prefix.
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
        for index, block in enumerate(self.chain):
            content = {
                key: value
                for key, value in block.items()
                if key != "hash"
            }

            if block["hash"] != hash_block(content):
                return False

            if index == 0:
                if block["previous_hash"] != "0" * 64:
                    return False
            else:
                previous = self.chain[index - 1]

                if block["index"] != index:
                    return False
                if block["previous_hash"] != previous["hash"]:
                    return False
                if not block["hash"].startswith("0" * DIFFICULTY):
                    return False

        return True
