
import unittest

from miner import mine_blocks


class MinerTests(unittest.TestCase):
    def test_mines_one_block(self):
        chain, blocks = mine_blocks("test-miner", 1)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["index"], 1)
        self.assertEqual(blocks[0]["transactions"][0]["amount"], 50)
        self.assertTrue(chain.is_valid())

    def test_mines_multiple_blocks(self):
        chain, blocks = mine_blocks("test-miner", 3)
        self.assertEqual(len(blocks), 3)
        self.assertEqual([b["index"] for b in blocks], [1, 2, 3])
        self.assertEqual(chain.issued_supply(), 150)
        self.assertTrue(chain.is_valid())

    def test_rejects_zero_blocks(self):
        with self.assertRaises(ValueError):
            mine_blocks("test-miner", 0)

    def test_rejects_empty_address(self):
        with self.assertRaises(ValueError):
            mine_blocks("", 1)


if __name__ == "__main__":
    unittest.main()
