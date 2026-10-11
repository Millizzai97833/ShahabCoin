
import os
import tempfile
import unittest

from blockchain import Blockchain
from storage import load_chain, save_chain
from wallet import create_wallet
from wallet_service import (
    create_signed_transfer,
    apply_transfer_block,
)
from wallet_dashboard import build_wallet_report


class WalletDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "chain.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_existing_reward_chain_is_compatible(self):
        chain = Blockchain()
        chain.add_block([], miner_address="ShahabMiner")
        chain.add_block([], miner_address="ShahabMiner")
        save_chain(chain, self.path)

        loaded = load_chain(self.path)
        report = build_wallet_report(loaded, "ShahabMiner")

        self.assertTrue(report["valid"])
        self.assertEqual(report["blocks"], 2)
        self.assertEqual(report["balances"]["ShahabMiner"], 100)
        self.assertEqual(len(report["history"]), 2)

    def test_transfer_and_balances_survive_reload(self):
        chain = Blockchain()
        private_key, public_bytes, _, sender = create_wallet()
        chain.add_block([], miner_address=sender)

        transfer = create_signed_transfer(
            private_key,
            public_bytes,
            "recipient-demo",
            12,
            0,
        )
        apply_transfer_block(
            chain, transfer, miner_address="demo-miner"
        )
        save_chain(chain, self.path)

        loaded = load_chain(self.path)
        report = build_wallet_report(loaded)

        self.assertEqual(report["balances"][sender], 38)
        self.assertEqual(report["balances"]["recipient-demo"], 12)
        self.assertEqual(report["balances"]["demo-miner"], 50)

        transfers = [
            item for item in report["history"]
            if item["type"] == "transfer"
        ]
        self.assertEqual(len(transfers), 1)
        self.assertEqual(transfers[0]["amount"], 12)

    def test_address_filter_shows_matching_history(self):
        chain = Blockchain()
        chain.add_block([], miner_address="ShahabMiner")
        chain.add_block([], miner_address="OtherMiner")

        report = build_wallet_report(chain, "OtherMiner")

        self.assertEqual(report["balances"]["OtherMiner"], 50)
        self.assertTrue(report["history"])
        self.assertTrue(
            all(
                item["from"] == "OtherMiner"
                or item["to"] == "OtherMiner"
                for item in report["history"]
            )
        )


if __name__ == "__main__":
    unittest.main()
