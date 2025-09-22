"""
Smart Budgeting App - Transaction Repository Layer

This module implements the Repository pattern for transaction data access.
It provides a clean abstraction layer between the business logic and data storage,
enabling easier testing, better separation of concerns, and potential future
data source changes.

The repository pattern provides:
- Abstraction over data storage mechanisms
- Consistent interface for data operations
- Type safety and validation
- Error handling and conversion
- Query flexibility with filters

Key Features:
- Full CRUD operations for transactions
- Flexible querying with filters
- Date range and category-based searches
- Balance and count operations
- Existence checking
- Error handling with boolean return values

Author: Smart Budgeting Team
Version: 2.0.0
"""

# Standard library imports
import datetime
from typing import List, Optional, Dict, Any

# Local application imports
from models import Transaction, Account, InvalidTransactionError

# ============================================================================
# TRANSACTION REPOSITORY CLASS
# ============================================================================

class TransactionRepository:
    """
    Repository pattern implementation for transaction data access.

    This class provides a clean abstraction layer over the Account model,
    offering a consistent interface for all transaction data operations.
    It handles error conversion and provides additional query capabilities.

    Key Benefits:
    - Decouples business logic from data storage
    - Provides consistent error handling
    - Enables easier testing with dependency injection
    - Supports future data source changes
    - Offers flexible querying options

    Attributes:
    - account (Account): The underlying account instance for data storage
    """

    def __init__(self, account: Account):
        """
        Initialize the repository with an account instance.

        Args:
            account (Account): Account instance for transaction storage
        """
        self.account = account  # Underlying account for data operations

    def save(self, transaction: Transaction) -> Transaction:
        """
        Save a new transaction to the repository.

        This method adds a new transaction to the persistent storage.
        The transaction will be assigned a unique ID automatically.

        Args:
            transaction (Transaction): The transaction to save

        Returns:
            Transaction: The saved transaction with assigned ID
        """
        self.account.add_transaction(transaction)
        return transaction

    def find_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Find a specific transaction by its unique ID.

        Args:
            transaction_id (int): Unique identifier of the transaction

        Returns:
            Transaction or None: The transaction if found, None otherwise
        """
        return self.account.get_transaction_by_id(transaction_id)

    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Transaction]:
        """
        Retrieve all transactions with optional filtering.

        This method provides flexible transaction retrieval with support
        for various filter criteria including date ranges and categories.

        Args:
            filters (dict, optional): Filter criteria as keyword arguments
                - start_date (datetime.date): Include only transactions on/after this date
                - end_date (datetime.date): Include only transactions on/before this date
                - category (str): Include only transactions in this category

        Returns:
            list: List of Transaction objects matching the filter criteria
        """
        return self.account.list_transactions(**(filters or {}))

    def find_by_date_range(self, start_date: datetime.date,
                          end_date: Optional[datetime.date] = None) -> List[Transaction]:
        """
        Find transactions within a specific date range.

        This method is optimized for date-based queries and is commonly
        used for monthly reports, analytics, and dashboard data.

        Args:
            start_date (datetime.date): Start date for the range (inclusive)
            end_date (datetime.date, optional): End date for the range (inclusive)
                                               If None, includes all transactions from start_date

        Returns:
            list: List of transactions within the specified date range
        """
        return self.account.list_transactions(
            start_date=start_date,
            end_date=end_date
        )

    def find_by_category(self, category: str) -> List[Transaction]:
        """
        Find all transactions in a specific category.

        This method is useful for category-based reporting and budget analysis.

        Args:
            category (str): Category name to filter by

        Returns:
            list: List of transactions in the specified category
        """
        return self.account.list_transactions(category=category)

    def update(self, transaction_id: int, **updates) -> bool:
        """
        Update an existing transaction with new values.

        This method provides a safe way to update transactions with
        automatic error handling. Only specified fields are updated.

        Args:
            transaction_id (int): ID of transaction to update
            **updates: Keyword arguments for fields to update
                      (date, amount, category, description)

        Returns:
            bool: True if update successful, False if transaction not found or invalid
        """
        try:
            # Attempt update with error handling
            self.account.update_transaction(transaction_id, **updates)
            return True  # Update successful
        except InvalidTransactionError:
            return False  # Update failed (transaction not found or invalid data)

    def delete(self, transaction_id: int) -> bool:
        """
        Delete a transaction from the repository.

        This method permanently removes a transaction from storage.
        The operation is safe and returns success/failure status.

        Args:
            transaction_id (int): ID of transaction to delete

        Returns:
            bool: True if deletion successful, False if transaction not found
        """
        try:
            # Attempt deletion with error handling
            self.account.delete_transaction(transaction_id)
            return True  # Deletion successful
        except InvalidTransactionError:
            return False  # Deletion failed (transaction not found)

    def get_balance(self) -> float:
        """
        Get the current account balance.

        This method provides a convenient way to get the total balance
        without needing to access the account directly.

        Returns:
            float: Current account balance (sum of all transaction amounts)
        """
        return self.account.get_balance()

    def count(self) -> int:
        """
        Get the total number of transactions in the repository.

        This method is useful for pagination, progress indicators,
        and general statistics about the transaction dataset.

        Returns:
            int: Total number of transactions stored
        """
        return len(self.account.transactions)

    def exists(self, transaction_id: int) -> bool:
        """
        Check if a transaction exists in the repository.

        This method provides a quick way to verify transaction existence
        without retrieving the full transaction object.

        Args:
            transaction_id (int): ID of transaction to check

        Returns:
            bool: True if transaction exists, False otherwise
        """
        return self.find_by_id(transaction_id) is not None
