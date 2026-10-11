
import json
from blockchain import (
    Blockchain,
    MAX_SUPPLY,
    TARGET_BLOCK_SECONDS,
)


def main():
    chain = Blockchain()

    chain.add_block([
        {
            "type": "demo",
            "message": "Welcome to ShahabCoin",
        }
    ])

    print("=== ShahabCoin (SHC) ===")
    print("Experimental blockchain prototype")
    print("Target supply:", f"{MAX_SUPPLY:,}", "SHC")
    print("Target block interval:", TARGET_BLOCK_SECONDS, "seconds")
    print("Blockchain valid:", chain.is_valid())
    print()
    print(json.dumps(chain.chain, indent=2))
    print()
    print("Prototype only: no real coins or mining rewards.")


if __name__ == "__main__":
    main()
