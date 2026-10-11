
import unittest

from blockchain import (
    Blockchain,
    MAX_SUPPLY,
    reward_for_height,
)


class MiningRewardTests(unittest.TestCase):
    def test_first_block_rewards_50_shc(self):
        chain = Blockchain()
        block = chain.add_block([], miner_address="miner-A")

        reward = block["transactions"][0]
        self.assertEqual(reward["amount"], 50)
        self.assertEqual(reward["to"], "miner-A")

    def test_reward_halves_after_210000_blocks(self):
        self.assertEqual(reward_for_height(1), 50)
        self.assertEqual(reward_for_height(210000), 50)
        self.assertEqual(reward_for_height(210001), 25)

    def test_reward_never_exceeds_supply_limit(self):
        self.assertEqual(
            reward_for_height(1, MAX_SUPPLY - 10), 10
        )
        self.assertEqual(reward_for_height(1, MAX_SUPPLY), 0)

    def test_tampered_reward_invalidates_chain(self):
        chain = Blockchain()
        block = chain.add_block([])
        block["transactions"][0]["amount"] = 5000
        self.assertFalse(chain.is_valid())


if __name__ == "__main__":
    unittest.main()
