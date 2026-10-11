
import unittest

from blockchain import Blockchain
from p2p import validate_chain_data


class PeerToPeerTests(unittest.TestCase):
    def test_valid_reward_chain_is_accepted(self):
        chain = Blockchain()
        chain.add_block([], miner_address="ShahabMiner")

        self.assertTrue(validate_chain_data(chain.chain))

    def test_genesis_only_chain_is_accepted(self):
        chain = Blockchain()

        self.assertTrue(validate_chain_data(chain.chain))

    def test_modified_block_is_rejected(self):
        chain = Blockchain()
        chain.add_block([], miner_address="ShahabMiner")
        data = [dict(block) for block in chain.chain]
        data[1]["transactions"] = []

        self.assertFalse(validate_chain_data(data))

    def test_empty_or_wrong_format_is_rejected(self):
        self.assertFalse(validate_chain_data([]))
        self.assertFalse(validate_chain_data({"chain": []}))
        self.assertFalse(validate_chain_data(None))


if __name__ == "__main__":
    unittest.main()
