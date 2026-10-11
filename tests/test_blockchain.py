
import unittest

from blockchain import Blockchain, make_genesis_block, hash_block


class BlockchainTests(unittest.TestCase):
    def test_genesis_hash(self):
        block = make_genesis_block()
        content = {k: v for k, v in block.items() if k != "hash"}
        self.assertEqual(block["hash"], hash_block(content))

    def test_add_block(self):
        chain = Blockchain()
        chain.add_block([{"message": "test"}])
        self.assertEqual(len(chain.chain), 2)
        self.assertTrue(chain.is_valid())

    def test_detect_modified_transaction(self):
        chain = Blockchain()
        chain.add_block([{"amount": 10}])
        chain.chain[1]["transactions"][0]["amount"] = 999
        self.assertFalse(chain.is_valid())


if __name__ == "__main__":
    unittest.main()
