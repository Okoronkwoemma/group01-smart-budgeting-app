import datetime
from typing import List, Optional, Dict, Any
from models import Transaction, Account, InvalidTransactionError

class TransactionRepository:
    """Repository pattern for transaction data access"""

    def __init__(self, account: Account):
        self.account = account

    def save(self, transaction: Transaction) -> Transaction:
        """Save a new transaction"""
        self.account.add_transaction(transaction)
        return transaction

    def find_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Find a transaction by its ID"""
        return self.account.get_transaction_by_id(transaction_id)

    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Transaction]:
        """Find all transactions with optional filters"""
        return self.account.list_transactions(**(filters or {}))

    def find_by_date_range(self, start_date: datetime.date,
                          end_date: Optional[datetime.date] = None) -> List[Transaction]:
        """Find transactions within a date range"""
        return self.account.list_transactions(
            start_date=start_date,
            end_date=end_date
        )

    def find_by_category(self, category: str) -> List[Transaction]:
        """Find transactions by category"""
        return self.account.list_transactions(category=category)

    def update(self, transaction_id: int, **updates) -> bool:
        """Update a transaction with new values"""
        try:
            self.account.update_transaction(transaction_id, **updates)
            return True
        except InvalidTransactionError:
            return False

    def delete(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        try:
            self.account.delete_transaction(transaction_id)
            return True
        except InvalidTransactionError:
            return False

    def get_balance(self) -> float:
        """Get current account balance"""
        return self.account.get_balance()

    def count(self) -> int:
        """Get total number of transactions"""
        return len(self.account.transactions)

    def exists(self, transaction_id: int) -> bool:
        """Check if a transaction exists"""
        return self.find_by_id(transaction_id) is not None
