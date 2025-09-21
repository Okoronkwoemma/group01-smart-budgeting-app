"""
Smart Budgeting App - Data Models

This module contains all the core data models and business logic for the Smart Budgeting application.
It implements the domain layer with proper validation, error handling, and data integrity checks.

The models follow Domain-Driven Design principles with:
- Rich domain objects with business logic
- Input validation and error handling
- Clean separation of concerns
- Immutable data where appropriate

Key Classes:
- InvalidTransactionError: Custom exception for transaction validation
- Transaction: Represents a financial transaction with full validation
- Account: Manages collections of transactions with business operations
- Budget: Handles budget planning and tracking

Author: Smart Budgeting Team
Version: 2.0.0
"""

# Standard library import for date/time operations
import datetime

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class InvalidTransactionError(Exception):
    """
    Custom exception class for transaction-related validation errors.

    This exception is raised when transaction data fails validation checks,
    providing clear error messages to help users correct their input.

    Common validation failures include:
    - Invalid date formats
    - Non-numeric amount values
    - Empty or invalid categories
    - Transaction not found errors
    """
    pass

# ============================================================================
# TRANSACTION MODEL
# ============================================================================

class Transaction:
    """
    Represents a financial transaction in the system.

    A Transaction is the core domain object representing any financial movement,
    whether it's income (positive amount) or expense (negative amount).

    Key Features:
    - Comprehensive input validation
    - Immutable date, amount, and category after creation
    - Optional description for additional context
    - Automatic ID assignment by Account
    - JSON serialization support

    Attributes:
    - date (datetime.date): When the transaction occurred
    - amount (float): Transaction amount (positive = income, negative = expense)
    - category (str): Transaction category (e.g., "Food", "Salary", "Transportation")
    - description (str): Optional description of the transaction
    - id (int): Unique identifier (assigned by Account)

    Validation Rules:
    - Date must be a datetime.date instance
    - Amount must be numeric (int or float)
    - Category must be non-empty string
    - Description is optional but recommended
    """

    def __init__(self, date, amount, category, description="", id=None):
        """
        Initialize a new Transaction with comprehensive validation.

        Args:
            date (datetime.date): Transaction date
            amount (float): Transaction amount
            category (str): Transaction category
            description (str, optional): Transaction description
            id (int, optional): Unique identifier

        Raises:
            InvalidTransactionError: If any validation fails
        """
        # Validate date parameter
        if not isinstance(date, datetime.date):
            raise InvalidTransactionError("date must be a datetime.date instance")

        # Validate amount parameter
        if not isinstance(amount, (int, float)):
            raise InvalidTransactionError("amount must be a number")

        # Validate category parameter
        if not isinstance(category, str) or not category:
            raise InvalidTransactionError("category must be a non-empty string")

        # Set instance attributes after successful validation
        self.date = date                    # Transaction date (immutable)
        self.amount = amount                # Transaction amount (immutable)
        self.category = category            # Transaction category (immutable)
        self.description = description      # Transaction description (mutable)
        self.id = id                        # Unique identifier (set by Account)

    def to_dict(self):
        """
        Convert transaction to dictionary representation for JSON serialization.

        This method is used by API endpoints to return transaction data
        in a format suitable for web clients and external integrations.

        Returns:
            dict: Dictionary representation of the transaction
        """
        return {
            "date": self.date.isoformat(),    # ISO format date string
            "amount": self.amount,             # Numeric amount value
            "category": self.category,         # Category string
            "description": self.description,   # Description text
        }

# ============================================================================
# ACCOUNT MODEL
# ============================================================================

class Account:
    """
    Manages a collection of financial transactions with business operations.

    The Account class serves as an aggregate root for transactions, providing
    high-level operations like balance calculation, transaction management,
    and filtering capabilities.

    Key Features:
    - Automatic ID assignment for transactions
    - Comprehensive transaction management (CRUD operations)
    - Flexible filtering by date range and category
    - Balance calculation across all transactions
    - Data integrity and validation

    Attributes:
    - transactions (list): Collection of Transaction objects
    - next_id (int): Counter for automatic ID assignment
    """

    def __init__(self):
        """
        Initialize a new Account with empty transaction collection.

        The account starts empty and grows as transactions are added.
        IDs are automatically assigned starting from 1.
        """
        self.transactions = []  # Storage for all transactions
        self.next_id = 1        # Next available transaction ID

    def add_transaction(self, transaction):
        """
        Add a new transaction to the account with automatic ID assignment.

        This method performs validation to ensure only valid Transaction
        instances are added to the account.

        Args:
            transaction (Transaction): The transaction to add

        Raises:
            InvalidTransactionError: If transaction is not a Transaction instance
        """
        # Validate that we're adding a proper Transaction object
        if not isinstance(transaction, Transaction):
            raise InvalidTransactionError("Must add a Transaction instance")

        # Assign unique ID and increment counter for next transaction
        transaction.id = self.next_id
        self.next_id += 1

        # Add transaction to collection
        self.transactions.append(transaction)

    def list_transactions(self, start_date=None, end_date=None, category=None):
        """
        Retrieve transactions with optional filtering.

        This method provides flexible transaction retrieval with multiple
        filter criteria that can be combined.

        Args:
            start_date (datetime.date, optional): Include only transactions on/after this date
            end_date (datetime.date, optional): Include only transactions on/before this date
            category (str, optional): Include only transactions in this category

        Returns:
            list: Filtered list of Transaction objects
        """
        # Start with all transactions
        results = self.transactions

        # Apply date range filter if specified
        if start_date:
            results = [t for t in results if t.date >= start_date]

        # Apply end date filter if specified
        if end_date:
            results = [t for t in results if t.date <= end_date]

        # Apply category filter if specified
        if category:
            results = [t for t in results if t.category == category]

        return results

    def get_balance(self):
        """
        Calculate the current account balance.

        Balance is calculated by summing all transaction amounts.
        Positive amounts (income) increase the balance, negative amounts
        (expenses) decrease it.

        Returns:
            float: Current account balance
        """
        return sum(t.amount for t in self.transactions)

    def get_transaction_by_id(self, id):
        """
        Retrieve a specific transaction by its unique ID.

        Args:
            id (int): Transaction ID to search for

        Returns:
            Transaction or None: The transaction if found, None otherwise
        """
        # Linear search through transactions (suitable for small datasets)
        for t in self.transactions:
            if t.id == id:
                return t
        return None  # Transaction not found

    def update_transaction(self, id, date=None, amount=None, category=None, description=None):
        """
        Update an existing transaction with new values.

        This method allows partial updates - only specified parameters
        are updated, leaving others unchanged.

        Args:
            id (int): ID of transaction to update
            date (datetime.date, optional): New date
            amount (float, optional): New amount
            category (str, optional): New category
            description (str, optional): New description

        Raises:
            InvalidTransactionError: If transaction not found or validation fails
        """
        # Find the transaction to update
        transaction = self.get_transaction_by_id(id)
        if not transaction:
            raise InvalidTransactionError(f"Transaction with id {id} not found")

        # Update only the specified fields with validation
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
        """
        Remove a transaction from the account.

        Args:
            id (int): ID of transaction to delete

        Returns:
            bool: True if transaction was deleted, False if not found
        """
        # Find the transaction to delete
        transaction = self.get_transaction_by_id(id)
        if not transaction:
            return False  # Transaction not found

        # Remove transaction from collection
        self.transactions.remove(transaction)
        return True  # Successfully deleted

# ============================================================================
# BUDGET MODEL
# ============================================================================

class Budget:
    """
    Manages budget planning and tracking for different categories.

    The Budget class helps users plan and monitor their spending by category.
    It provides functionality to set budget limits and track remaining budget.

    Key Features:
    - Category-based budget setting
    - Budget validation (no negative budgets)
    - Remaining budget calculation
    - Monthly budget tracking

    Attributes:
    - monthly_budgets (dict): Maps category names to budget amounts
    """

    def __init__(self):
        """
        Initialize a new Budget with empty budget collection.

        Budgets are stored as a dictionary mapping category names to amounts.
        """
        self.monthly_budgets = {}  # Dictionary: category -> amount

    def set_budget(self, category, amount):
        """
        Set a monthly budget for a specific category.

        Args:
            category (str): Budget category name
            amount (float): Budget amount (must be non-negative)

        Raises:
            ValueError: If budget amount is negative
        """
        # Validate that budget amount is non-negative
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")

        # Set the budget for this category
        self.monthly_budgets[category] = amount

    def get_budget(self, category):
        """
        Retrieve the budget amount for a specific category.

        Args:
            category (str): Budget category name

        Returns:
            float: Budget amount, or 0 if no budget set for category
        """
        return self.monthly_budgets.get(category, 0)

    def get_remaining(self, category, spent):
        """
        Calculate remaining budget for a category.

        Args:
            category (str): Budget category name
            spent (float): Amount already spent in this category

        Returns:
            float: Remaining budget (budget - spent)
        """
        return self.get_budget(category) - spent
