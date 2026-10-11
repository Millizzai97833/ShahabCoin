
import argparse

from blockchain import Blockchain


def mine_blocks(miner_address="demo-miner", count=1):
    """Mine blocks locally for the ShahabCoin prototype."""
    if not isinstance(miner_address, str) or not miner_address.strip():
        raise ValueError("Miner address cannot be empty")

    if type(count) is not int or count < 1:
        raise ValueError("Block count must be a positive integer")

    chain = Blockchain()
    mined_blocks = []

    for _ in range(count):
        block = chain.add_block([], miner_address=miner_address)
        mined_blocks.append(block)

    if not chain.is_valid():
        raise RuntimeError("Blockchain validation failed")

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
        help="Number of blocks to mine (default: 1)",
    )
    args = parser.parse_args()

    try:
        chain, blocks = mine_blocks(args.address, args.blocks)
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))

    print("=== ShahabCoin Test Miner ===")
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
    print("Blocks in local chain:", len(chain.chain) - 1)
    print("Recorded mining rewards:", chain.issued_supply(), "SHC")
    print("Blockchain valid:", chain.is_valid())
    print("Simulation only: no real coins or money were created.")


if __name__ == "__main__":
    main()
