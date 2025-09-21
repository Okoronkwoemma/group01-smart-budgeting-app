import unittest
from flask import Flask
from models import Transaction, Account, Budget, InvalidTransactionError
from services.transaction_service import TransactionService
from repositories.transaction_repository import TransactionRepository
from factories.app_factory import AppFactory
from utils import parse_csv_line
import datetime

class TestTransaction(unittest.TestCase):
    def test_valid_transaction(self):
        date = datetime.date(2023, 10, 1)
        t = Transaction(date, 100.0, "Income", "Salary")
        self.assertEqual(t.amount, 100.0)
        self.assertEqual(t.category, "Income")

    def test_invalid_date(self):
        with self.assertRaises(InvalidTransactionError):
            Transaction("2023-10-01", 100.0, "Income")

    def test_invalid_amount(self):
        date = datetime.date(2023, 10, 1)
        with self.assertRaises(InvalidTransactionError):
            Transaction(date, "100", "Income")

    def test_invalid_category(self):
        date = datetime.date(2023, 10, 1)
        with self.assertRaises(InvalidTransactionError):
            Transaction(date, 100.0, "")

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account()

    def test_add_transaction(self):
        date = datetime.date(2023, 10, 1)
        t = Transaction(date, 100.0, "Income")
        self.account.add_transaction(t)
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.get_balance(), 100.0)

    def test_list_transactions(self):
        date1 = datetime.date(2023, 10, 1)
        date2 = datetime.date(2023, 10, 2)
        t1 = Transaction(date1, 100.0, "Income")
        t2 = Transaction(date2, -50.0, "Groceries")
        self.account.add_transaction(t1)
        self.account.add_transaction(t2)
        results = self.account.list_transactions(category="Groceries")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].amount, -50.0)

class TestBudget(unittest.TestCase):
    def setUp(self):
        self.budget = Budget()

    def test_set_budget(self):
        self.budget.set_budget("Groceries", 500.0)
        self.assertEqual(self.budget.get_budget("Groceries"), 500.0)

    def test_get_remaining(self):
        self.budget.set_budget("Groceries", 500.0)
        remaining = self.budget.get_remaining("Groceries", 200.0)
        self.assertEqual(remaining, 300.0)

class TestUtils(unittest.TestCase):
    def test_parse_csv_line(self):
        line = "2023-10-01,-50.00,Groceries,Weekly shop"
        date, amount, category, description = parse_csv_line(line)
        self.assertEqual(date, datetime.date(2023, 10, 1))
        self.assertEqual(amount, -50.0)
        self.assertEqual(category, "Groceries")
        self.assertEqual(description, "Weekly shop")

    def test_parse_csv_line_us_date(self):
        line = "10/01/2023,-50.00,Groceries"
        date, amount, category, description = parse_csv_line(line)
        self.assertEqual(date, datetime.date(2023, 10, 1))
        self.assertEqual(amount, -50.0)
        self.assertEqual(category, "Groceries")
        self.assertEqual(description, "")

class TestTransactionService(unittest.TestCase):
    def setUp(self):
        self.account = Account()
        self.budget = Budget()
        self.service = TransactionService(self.account, self.budget)

    def test_create_transaction(self):
        date = datetime.date(2023, 10, 1)
        transaction = self.service.create_transaction(date, 100.0, "Income", "Salary")
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(self.service.get_balance(), 100.0)

    def test_get_monthly_spending(self):
        # Add some transactions
        date = datetime.date(2023, 10, 1)
        self.service.create_transaction(date, -50.0, "Groceries")
        self.service.create_transaction(date, -25.0, "Entertainment")
        self.service.create_transaction(date, 1000.0, "Income")

        spending = self.service.get_monthly_spending(2023, 10)
        self.assertEqual(spending, 75.0)

    def test_get_category_totals(self):
        date = datetime.date(2023, 10, 1)
        self.service.create_transaction(date, -50.0, "Groceries")
        self.service.create_transaction(date, -25.0, "Groceries")
        self.service.create_transaction(date, 1000.0, "Income")

        totals = self.service.get_category_totals(2023, 10)
        self.assertEqual(totals["Groceries"], -75.0)
        self.assertEqual(totals["Income"], 1000.0)

class TestTransactionRepository(unittest.TestCase):
    def setUp(self):
        self.account = Account()
        self.repository = TransactionRepository(self.account)

    def test_save_transaction(self):
        date = datetime.date(2023, 10, 1)
        transaction = Transaction(date, 100.0, "Income")
        saved = self.repository.save(transaction)

        self.assertEqual(self.repository.count(), 1)
        self.assertEqual(saved.id, 1)

    def test_find_by_id(self):
        date = datetime.date(2023, 10, 1)
        transaction = Transaction(date, 100.0, "Income")
        self.repository.save(transaction)

        found = self.repository.find_by_id(1)
        self.assertIsNotNone(found)
        self.assertEqual(found.amount, 100.0)

    def test_find_all(self):
        date = datetime.date(2023, 10, 1)
        t1 = Transaction(date, 100.0, "Income")
        t2 = Transaction(date, -50.0, "Groceries")

        self.repository.save(t1)
        self.repository.save(t2)

        all_transactions = self.repository.find_all()
        self.assertEqual(len(all_transactions), 2)

    def test_update_transaction(self):
        date = datetime.date(2023, 10, 1)
        transaction = Transaction(date, 100.0, "Income")
        self.repository.save(transaction)

        updated = self.repository.update(1, amount=200.0, category="Salary")
        self.assertTrue(updated)

        found = self.repository.find_by_id(1)
        self.assertEqual(found.amount, 200.0)
        self.assertEqual(found.category, "Salary")

    def test_delete_transaction(self):
        date = datetime.date(2023, 10, 1)
        transaction = Transaction(date, 100.0, "Income")
        self.repository.save(transaction)

        deleted = self.repository.delete(1)
        self.assertTrue(deleted)
        self.assertEqual(self.repository.count(), 0)

class TestAppFactory(unittest.TestCase):
    def test_create_full_app(self):
        components = AppFactory.create_full_app()

        self.assertIn('app', components)
        self.assertIn('account', components)
        self.assertIn('budget', components)
        self.assertIn('transaction_service', components)
        self.assertIn('repository', components)

        self.assertIsInstance(components['app'], Flask)
        self.assertIsInstance(components['account'], Account)
        self.assertIsInstance(components['budget'], Budget)

if __name__ == '__main__':
    unittest.main()
