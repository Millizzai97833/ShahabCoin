
import unittest

from blockchain import Blockchain
from wallet import create_wallet
from wallet_service import (
    calculate_balances,
    create_signed_transfer,
    apply_transfer_block,
)


class WalletServiceTests(unittest.TestCase):
    def setUp(self):
        self.chain = Blockchain()
        self.private_key, self.public_bytes, _, self.address = (
            create_wallet()
        )
        self.chain.add_block([], miner_address=self.address)

    def test_mining_reward_appears_in_balance(self):
        balances = calculate_balances(self.chain)
        self.assertEqual(balances[self.address], 50)

    def test_valid_transfer_updates_balances(self):
        recipient = "recipient-demo"

        transfer = create_signed_transfer(
            self.private_key,
            self.public_bytes,
            recipient,
            12,
            0,
        )

        apply_transfer_block(
            self.chain, transfer, miner_address="demo-miner"
        )

        balances = calculate_balances(self.chain)
        self.assertEqual(balances[self.address], 38)
        self.assertEqual(balances[recipient], 12)

    def test_overspending_is_rejected(self):
        transfer = create_signed_transfer(
            self.private_key,
            self.public_bytes,
            "recipient-demo",
            999,
            0,
        )

        with self.assertRaises(ValueError):
            apply_transfer_block(
                self.chain, transfer, miner_address="demo-miner"
            )

    def test_replayed_transfer_is_rejected(self):
        transfer = create_signed_transfer(
            self.private_key,
            self.public_bytes,
            "recipient-demo",
            10,
            0,
        )

        apply_transfer_block(
            self.chain, transfer, miner_address="demo-miner"
        )

        with self.assertRaises(ValueError):
            apply_transfer_block(
                self.chain, transfer, miner_address="demo-miner"
            )


if __name__ == "__main__":
    unittest.main()
