
import os
import tempfile
import unittest

from blockchain import Blockchain
from storage import save_chain, load_chain
from wallet_view import wallet_reward_history


class WalletViewTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "chain.json")

        self.chain = Blockchain()
        self.chain.add_block([], miner_address="ShahabMiner")
        self.chain.add_block([], miner_address="OtherMiner")
        self.chain.add_block([], miner_address="ShahabMiner")

        save_chain(self.chain, self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_shows_only_matching_rewards(self):
        loaded = load_chain(self.path)
        history = wallet_reward_history(loaded, "ShahabMiner")

        self.assertEqual(len(history), 2)
        self.assertEqual(
            sum(item["amount"] for item in history), 100
        )

    def test_other_miner_has_separate_history(self):
        loaded = load_chain(self.path)
        history = wallet_reward_history(loaded, "OtherMiner")

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["amount"], 50)

    def test_empty_address_rejected(self):
        with self.assertRaises(ValueError):
            wallet_reward_history(self.chain, "")


if __name__ == "__main__":
    unittest.main()
