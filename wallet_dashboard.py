
import argparse

from storage import load_chain
from wallet_service import calculate_balances


def build_wallet_report(blockchain, address=None):
    """Build a read-only report from the saved blockchain."""
    if address is not None:
        if not isinstance(address, str) or not address.strip():
            raise ValueError("Address cannot be empty")

    # Reconstruct balances and validate the chain and signed transfers.
    balances = calculate_balances(blockchain)
    history = []

    for block in blockchain.chain[1:]:
        for tx in block["transactions"]:
            if tx.get("type") == "mining_reward":
                entry = {
                    "block": block["index"],
                    "type": "mining_reward",
                    "from": "NETWORK",
                    "to": tx["to"],
                    "amount": tx["amount"],
                    "currency": "SHC",
                }
            else:
                entry = {
                    "block": block["index"],
                    "type": "transfer",
                    "from": tx["from"],
                    "to": tx["to"],
                    "amount": tx["amount"],
                    "currency": tx["currency"],
                    "nonce": tx["nonce"],
                }

            if address is None or address in (
                entry["from"], entry["to"]
            ):
                history.append(entry)

    return {
        "valid": True,
        "blocks": len(blockchain.chain) - 1,
        "balances": balances,
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser(
        description="ShahabCoin read-only wallet dashboard"
    )
    parser.add_argument(
        "--file",
        default="shahabcoin_chain.json",
        help="Saved blockchain JSON file",
    )
    parser.add_argument(
        "--address",
        default=None,
        help="Optional address to inspect",
    )
    args = parser.parse_args()

    try:
        blockchain = load_chain(args.file)
        report = build_wallet_report(blockchain, args.address)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.error(str(error))

    print("=== ShahabCoin Wallet Dashboard ===")
    print("Saved chain:", args.file)
    print("Blocks after genesis:", report["blocks"])
    print("Blockchain and transfer history valid:", report["valid"])

    print("\n=== Balances ===")
    if args.address is not None:
        print(
            args.address,
            ":",
            report["balances"].get(args.address, 0),
            "SHC",
        )
    elif report["balances"]:
        for wallet_address, balance in sorted(
            report["balances"].items()
        ):
            print(wallet_address, ":", balance, "SHC")
    else:
        print("No balances recorded.")

    print("\n=== Transaction History ===")
    if not report["history"]:
        print("No matching history entries.")
    else:
        for entry in report["history"]:
            print(
                f"Block {entry['block']} | "
                f"{entry['type']} | "
                f"{entry['from']} -> {entry['to']} | "
                f"{entry['amount']} {entry['currency']}"
            )

    print("\nRead-only report; no transactions were created.")
    print("Prototype SHC is not real money or a spendable asset.")


if __name__ == "__main__":
    main()
              
