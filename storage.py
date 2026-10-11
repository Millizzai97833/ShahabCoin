
import json
import os

from blockchain import Blockchain


def save_chain(blockchain, filename="shahabcoin_chain.json"):
    """Save a valid blockchain to a JSON file."""
    if not blockchain.is_valid():
        raise ValueError("Cannot save an invalid blockchain")

    temporary = filename + ".tmp"

    try:
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(blockchain.chain, file, indent=2)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary, filename)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def load_chain(filename="shahabcoin_chain.json"):
    """Load a saved blockchain or create a new one if no file exists."""
    if not os.path.exists(filename):
        return Blockchain()

    with open(filename, "r", encoding="utf-8") as file:
        saved_chain = json.load(file)

    if not isinstance(saved_chain, list) or not saved_chain:
        raise ValueError("Saved blockchain has an invalid format")

    blockchain = Blockchain()
    blockchain.chain = saved_chain

    if not blockchain.is_valid():
        raise ValueError("Saved blockchain failed validation")

    return blockchain
