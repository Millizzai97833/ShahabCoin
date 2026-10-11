
import unittest

from blockchain import Blockchain, hash_block
from wallet import create_wallet
from wallet_service import create_signed_transfer


class BlockchainTests(unittest.TestCase):
    def test_genesis_hash(self):
        chain = Blockchain()
        genesis = chain.chain[0]

        content = {
            key: value for key, value in genesis.items()
            if key != "hash"
        }

        self.assertEqual(genesis["hash"], hash_block(content))
        self.assertTrue(chain.is_valid())

    def test_add_block(self):
        chain = Blockchain()
        block = chain.add_block([], miner_address="test-miner")

        self.assertEqual(block["index"], 1)
        self.assertTrue(chain.is_valid())

    def test_detect_modified_transaction(self):
        chain = Blockchain()
        private_key, public_bytes, _, sender = create_wallet()

        chain.add_block([], miner_address=sender)

        transfer = create_signed_transfer(
            private_key,
            public_bytes,
            "recipient-demo",
            10,
            0,
        )
        chain.add_block([transfer], miner_address="test-miner")

        chain.chain[2]["transactions"][1]["amount"] = 11

        self.assertFalse(chain.is_valid())

    def test_reject_invalid_proof_of_work(self):
        chain = Blockchain()
        chain.add_block([], miner_address="test-miner")

        chain.chain[1]["nonce"] += 1

        self.assertFalse(chain.is_valid())

    def test_reject_unsigned_transfer(self):
        chain = Blockchain()

        unsigned = {
            "from": "Alice",
            "to": "Bob",
            "amount": 10,
            "nonce": 0,
            "currency": "SHC",
        }

        with self.assertRaises(ValueError):
            chain.add_block([unsigned], miner_address="test-miner")

        self.assertEqual(len(chain.chain), 1)
        self.assertTrue(chain.is_valid())


if __name__ == "__main__":
    unittest.main()
    
