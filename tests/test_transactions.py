
import unittest

from transactions import TransactionLedger
from wallet import create_wallet, sign_transaction


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.private, self.public, _, self.address = create_wallet()
        self.ledger = TransactionLedger({self.address: 100})

    def make_transaction(self, amount=25, nonce=0):
        tx = {
            "from": self.address,
            "to": "recipient-demo",
            "amount": amount,
            "nonce": nonce,
            "currency": "SHC",
        }
        return tx, sign_transaction(self.private, tx)

    def test_valid_transfer(self):
        tx, sig = self.make_transaction()
        ok, _ = self.ledger.apply(tx, self.public, sig)

        self.assertTrue(ok)
        self.assertEqual(self.ledger.balances[self.address], 75)
        self.assertEqual(self.ledger.balances["recipient-demo"], 25)

    def test_insufficient_balance(self):
        tx, sig = self.make_transaction(amount=101)
        ok, _ = self.ledger.apply(tx, self.public, sig)
        self.assertFalse(ok)
        self.assertEqual(self.ledger.balances[self.address], 100)

    def test_replayed_nonce_rejected(self):
        tx, sig = self.make_transaction()
        self.assertTrue(self.ledger.apply(tx, self.public, sig)[0])
        self.assertFalse(self.ledger.apply(tx, self.public, sig)[0])

    def test_tampered_amount_rejected(self):
        tx, sig = self.make_transaction()
        tx["amount"] = 50
        self.assertFalse(self.ledger.apply(tx, self.public, sig)[0])


if __name__ == "__main__":
    unittest.main()
