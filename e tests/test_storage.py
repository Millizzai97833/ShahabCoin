
import json
import os
import tempfile
import unittest

from blockchain import Blockchain
from storage import load_chain, save_chain


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(
            self.temp_dir.name, "test_chain.json"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_creates_new_chain(self):
        chain = load_chain(self.path)
        self.assertEqual(len(chain.chain), 1)
        self.assertTrue(chain.is_valid())

    def test_saved_chain_survives_reload(self):
        chain = Blockchain()
        chain.add_block([], miner_address="test-miner")
        save_chain(chain, self.path)

        loaded = load_chain(self.path)
        self.assertEqual(loaded.chain, chain.chain)
        self.assertEqual(loaded.issued_supply(), 50)
        self.assertTrue(loaded.is_valid())

    def test_tampered_saved_chain_is_rejected(self):
        chain = Blockchain()
        chain.add_block([], miner_address="test-miner")
        save_chain(chain, self.path)

        with open(self.path, "r", encoding="utf-8") as file:
            data = json.load(file)

        data[1]["transactions"][0]["amount"] = 5000

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file)

        with self.assertRaises(ValueError):
            load_chain(self.path)


if __name__ == "__main__":
    unittest.main()
  
