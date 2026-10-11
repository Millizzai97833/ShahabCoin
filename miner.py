
import argparse

from blockchain import Blockchain
from storage import load_chain, save_chain


def mine_blocks(
    miner_address="demo-miner",
    count=1,
    storage_path=None,
):
    """Mine blocks locally, optionally loading and saving a chain."""
    if not isinstance(miner_address, str) or not miner_address.strip():
        raise ValueError("Miner address cannot be empty")

    if type(count) is not int or count < 1:
        raise ValueError("Block count must be a positive integer")

    chain = load_chain(storage_path) if storage_path else Blockchain()
    mined_blocks = []

    for _ in range(count):
        block = chain.add_block([], miner_address=miner_address)
        mined_blocks.append(block)

    if not chain.is_valid():
        raise RuntimeError("Blockchain validation failed")

    if storage_path:
        save_chain(chain, storage_path)

    return chain, mined_blocks


def main():
    parser = argparse.ArgumentParser(
        description="Mine test blocks for ShahabCoin"
    )
    parser.add_argument(
        "--address",
        default="demo-miner",
        help="Miner label/address for this local test",
    )
    parser.add_argument(
        "--blocks",
        type=int,
        default=1,
        help="Number of blocks to mine",
    )
    parser.add_argument(
        "--file",
        default="shahabcoin_chain.json",
        help="Path to the saved blockchain JSON file",
    )
    args = parser.parse_args()

    try:
        chain, blocks = mine_blocks(
            args.address,
            args.blocks,
            args.file,
        )
    except (ValueError, RuntimeError, OSError) as error:
        parser.error(str(error))

    print("=== ShahabCoin Persistent Test Miner ===")
    print("Miner:", args.address)

    for block in blocks:
        reward = sum(
            tx["amount"]
            for tx in block["transactions"]
            if tx.get("type") == "mining_reward"
        )
        print()
        print("Block height:", block["index"])
        print("Reward:", reward, "SHC")
        print("Nonce:", block["nonce"])
        print("Block hash:", block["hash"])

    print()
    print("Total blocks after genesis:", len(chain.chain) - 1)
    print("Recorded mining rewards:", chain.issued_supply(), "SHC")
    print("Blockchain valid:", chain.is_valid())
    print("Saved to:", args.file)
    print("Simulation only: no real coins or money were created.")


if __name__ == "__main__":
    main()
    
