import datetime
from models import Transaction, Account, Budget, InvalidTransactionError

class TransactionService:
    """Service class for handling transaction-related business logic"""

    def __init__(self, account: Account, budget: Budget = None):
        self.account = account
        self.budget = budget

    def create_transaction(self, date, amount, category, description=""):
        """Create and save a new transaction"""
        transaction = Transaction(date, amount, category, description)
        self.account.add_transaction(transaction)
        return transaction

    def get_monthly_spending(self, year=None, month=None):
        """Calculate total spending for a specific month"""
        if year is None or month is None:
            today = datetime.date.today()
            year, month = today.year, today.month

        start_month = datetime.date(year, month, 1)
        if month == 12:
            end_month = datetime.date(year + 1, 1, 1)
        else:
            end_month = datetime.date(year, month + 1, 1)

        monthly_transactions = self.account.list_transactions(
            start_date=start_month,
            end_date=end_month
        )
        return sum(abs(t.amount) for t in monthly_transactions if t.amount < 0)

    def get_monthly_income(self, year=None, month=None):
        """Calculate total income for a specific month"""
        if year is None or month is None:
            today = datetime.date.today()
            year, month = today.year, today.month

        start_month = datetime.date(year, month, 1)
        if month == 12:
            end_month = datetime.date(year + 1, 1, 1)
        else:
            end_month = datetime.date(year, month + 1, 1)

        monthly_transactions = self.account.list_transactions(
            start_date=start_month,
            end_date=end_month
        )
        return sum(t.amount for t in monthly_transactions if t.amount > 0)

    def get_category_totals(self, year=None, month=None):
        """Get spending totals by category for a specific month"""
        if year is None or month is None:
            today = datetime.date.today()
            year, month = today.year, today.month

        start_month = datetime.date(year, month, 1)
        if month == 12:
            end_month = datetime.date(year + 1, 1, 1)
        else:
            end_month = datetime.date(year, month + 1, 1)

        monthly_transactions = self.account.list_transactions(
            start_date=start_month,
            end_date=end_month
        )

        category_totals = {}
        for t in monthly_transactions:
            category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

        return category_totals

    def get_category_spending(self, year=None, month=None):
        """Get spending amounts by category (positive values for pie chart)"""
        category_totals = self.get_category_totals(year, month)
        # Only include categories with negative amounts (expenses)
        return {k: abs(v) for k, v in category_totals.items() if v < 0}

    def get_balance(self):
        """Get current account balance"""
        return self.account.get_balance()

    def get_transaction_by_id(self, transaction_id):
        """Get a specific transaction by ID"""
        return self.account.get_transaction_by_id(transaction_id)

    def update_transaction(self, transaction_id, **updates):
        """Update a transaction with new values"""
        self.account.update_transaction(transaction_id, **updates)

    def delete_transaction(self, transaction_id):
        """Delete a transaction"""
        self.account.delete_transaction(transaction_id)

    def import_transactions_from_csv(self, csv_content):
        """Import multiple transactions from CSV content"""
        from utils import parse_csv_line

        lines = csv_content.strip().splitlines()
        imported = 0
        errors = []

        for i, line in enumerate(lines):
            try:
                date, amount, category, description = parse_csv_line(line)
                self.create_transaction(date, amount, category, description)
                imported += 1
            except Exception as e:
                errors.append(f"Line {i+1}: {e}")

        return imported, errors

    def get_budget_status(self, category):
        """Get budget status for a category"""
        if not self.budget:
            return None

        spent = abs(self.get_category_totals().get(category, 0))
        budget_amount = self.budget.get_budget(category)
        remaining = budget_amount - spent

        return {
            'budget': budget_amount,
            'spent': spent,
            'remaining': remaining
        }
