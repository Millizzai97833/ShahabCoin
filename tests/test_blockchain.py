
import unittest

from blockchain import (
    Blockchain,
    DIFFICULTY,
    hash_block,
    make_genesis_block,
)


class BlockchainTests(unittest.TestCase):
    def test_genesis_hash(self):
        block = make_genesis_block()
        content = {k: v for k, v in block.items() if k != "hash"}
        self.assertEqual(block["hash"], hash_block(content))

    def test_add_block(self):
        chain = Blockchain()
        block = chain.add_block([{"message": "test"}])

        self.assertEqual(len(chain.chain), 2)
        self.assertTrue(chain.is_valid())
        self.assertTrue(
            block["hash"].startswith("0" * DIFFICULTY)
        )

    def test_detect_modified_transaction(self):
        chain = Blockchain()
        chain.add_block([{"amount": 10}])
        chain.chain[1]["transactions"][0]["amount"] = 999
        self.assertFalse(chain.is_valid())

    def test_reject_invalid_proof_of_work(self):
        chain = Blockchain()
        block = chain.add_block([{"message": "test"}])

        # Corrupt the proof-of-work hash.
        block["hash"] = "f" * 64
        self.assertFalse(chain.is_valid())


if __name__ == "__main__":
    unittest.main()
