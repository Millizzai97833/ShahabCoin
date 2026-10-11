
import unittest

from wallet import (
    create_wallet,
    sign_transaction,
    verify_transaction,
)


class WalletTests(unittest.TestCase):
    def test_valid_signature(self):
        private_key, public_bytes, _, address = create_wallet()
        transaction = {
            "from": address,
            "to": "test-recipient",
            "amount": 5,
            "currency": "SHC",
        }

        signature = sign_transaction(private_key, transaction)

        self.assertTrue(
            verify_transaction(public_bytes, transaction, signature)
        )

    def test_modified_amount_rejected(self):
        private_key, public_bytes, _, address = create_wallet()
        transaction = {
            "from": address,
            "to": "test-recipient",
            "amount": 5,
            "currency": "SHC",
        }

        signature = sign_transaction(private_key, transaction)
        transaction["amount"] = 500

        self.assertFalse(
            verify_transaction(public_bytes, transaction, signature)
        )


if __name__ == "__main__":
    unittest.main()
