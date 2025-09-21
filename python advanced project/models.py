import datetime

class InvalidTransactionError(Exception):
    pass

class Transaction:
    def __init__(self, date, amount, category, description="", id=None):
        if not isinstance(date, datetime.date):
            raise InvalidTransactionError("date must be a datetime.date instance")
        if not isinstance(amount, (int, float)):
            raise InvalidTransactionError("amount must be a number")
        if not isinstance(category, str) or not category:
            raise InvalidTransactionError("category must be a non-empty string")
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description
        self.id = id

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
        }

class Account:
    def __init__(self):
        self.transactions = []
        self.next_id = 1

    def add_transaction(self, transaction):
        if not isinstance(transaction, Transaction):
            raise InvalidTransactionError("Must add a Transaction instance")
        transaction.id = self.next_id
        self.next_id += 1
        self.transactions.append(transaction)

    def list_transactions(self, start_date=None, end_date=None, category=None):
        results = self.transactions
        if start_date:
            results = [t for t in results if t.date >= start_date]
        if end_date:
            results = [t for t in results if t.date <= end_date]
        if category:
            results = [t for t in results if t.category == category]
        return results

    def get_balance(self):
        return sum(t.amount for t in self.transactions)

    def get_transaction_by_id(self, id):
        for t in self.transactions:
            if t.id == id:
                return t
        return None

    def update_transaction(self, id, date=None, amount=None, category=None, description=None):
        transaction = self.get_transaction_by_id(id)
        if not transaction:
            raise InvalidTransactionError(f"Transaction with id {id} not found")
        if date is not None:
            if not isinstance(date, datetime.date):
                raise InvalidTransactionError("date must be a datetime.date instance")
            transaction.date = date
        if amount is not None:
            if not isinstance(amount, (int, float)):
                raise InvalidTransactionError("amount must be a number")
            transaction.amount = amount
        if category is not None:
            if not isinstance(category, str) or not category:
                raise InvalidTransactionError("category must be a non-empty string")
            transaction.category = category
        if description is not None:
            transaction.description = description

    def delete_transaction(self, id):
        transaction = self.get_transaction_by_id(id)
        if not transaction:
            raise InvalidTransactionError(f"Transaction with id {id} not found")
        self.transactions.remove(transaction)

class Budget:
    def __init__(self):
        self.monthly_budgets = {}  # category -> amount

    def set_budget(self, category, amount):
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")
        self.monthly_budgets[category] = amount

    def get_budget(self, category):
        return self.monthly_budgets.get(category, 0)

    def get_remaining(self, category, spent):
        return self.get_budget(category) - spent
