
import argparse

from storage import load_chain


def wallet_reward_history(blockchain, address):
    """Return recorded mining rewards for an address or miner label."""
    if not blockchain.is_valid():
        raise ValueError("Blockchain validation failed")

    if not isinstance(address, str) or not address.strip():
        raise ValueError("Address cannot be empty")

    history = []

    for block in blockchain.chain[1:]:
        for tx in block.get("transactions", []):
            if (
                isinstance(tx, dict)
                and tx.get("type") == "mining_reward"
                and tx.get("to") == address
            ):
                history.append({
                    "block": block["index"],
                    "amount": tx["amount"],
                    "hash": block["hash"],
                })

    return history


def main():
    parser = argparse.ArgumentParser(
        description="View ShahabCoin local mining rewards"
    )
    parser.add_argument(
        "--address",
        default="ShahabMiner",
        help="Miner label/address to inspect",
    )
    parser.add_argument(
        "--file",
        default="shahabcoin_chain.json",
        help="Path to the saved blockchain JSON file",
    )
    args = parser.parse_args()

    try:
        chain = load_chain(args.file)
        history = wallet_reward_history(chain, args.address)
    except (ValueError, OSError) as error:
        parser.error(str(error))

    total = sum(item["amount"] for item in history)

    print("=== ShahabCoin Wallet Viewer ===")
    print("Address/label:", args.address)
    print("Saved blocks:", len(chain.chain) - 1)
    print("Blockchain valid:", chain.is_valid())
    print("Recorded rewards:", total, "SHC")
    print("Reward entries:", len(history))

    if history:
        print("\n=== Mining Reward History ===")
        for item in history:
            print(
                f"Block {item['block']}: "
                f"+{item['amount']} SHC"
            )
            print("Hash:", item["hash"])
    else:
        print("No mining rewards found for this address.")

    print("\nRead-only local prototype.")
    print("This is not a spendable wallet balance.")


if __name__ == "__main__":
    main()
  
