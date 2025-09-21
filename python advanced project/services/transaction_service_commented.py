"""
Smart Budgeting App - Transaction Service Layer

This module implements the service layer for transaction-related business logic.
It acts as an intermediary between the web controllers and the data models,
providing high-level operations and business rules.

The service layer follows Domain-Driven Design principles by:
- Encapsulating business logic and validation rules
- Coordinating between multiple domain objects
- Providing a clean API for controllers to use
- Handling complex operations that span multiple models

Key Features:
- Transaction creation and management
- Financial calculations (spending, income, balance)
- Category-based analytics
- CSV import processing
- Budget integration
- Date range filtering

Author: Smart Budgeting Team
Version: 2.0.0
"""

# Standard library imports
import datetime

# Local application imports
from models import Transaction, Account, Budget, InvalidTransactionError

# ============================================================================
# TRANSACTION SERVICE CLASS
# ============================================================================

class TransactionService:
    """
    Service class for handling transaction-related business logic.

    This class serves as the main business logic layer, providing high-level
    operations for transaction management, financial calculations, and analytics.
    It coordinates between the Account, Budget, and Transaction models.

    Key Responsibilities:
    - Transaction lifecycle management (CRUD operations)
    - Financial calculations and analytics
    - Category-based reporting
    - CSV import processing
    - Budget integration and tracking

    Attributes:
    - account (Account): The account instance for transaction storage
    - budget (Budget, optional): The budget instance for budget tracking
    """

    def __init__(self, account: Account, budget: Budget = None):
        """
        Initialize the TransactionService with required dependencies.

        Args:
            account (Account): Account instance for transaction operations
            budget (Budget, optional): Budget instance for budget tracking
        """
        self.account = account  # Account for transaction storage and operations
        self.budget = budget    # Optional budget for budget-related features

    def create_transaction(self, date, amount, category, description=""):
        """
        Create and save a new transaction with full validation.

        This method handles the complete transaction creation process:
        1. Creates Transaction object with validation
        2. Adds transaction to account with ID assignment
        3. Returns the created transaction

        Args:
            date (datetime.date): Transaction date
            amount (float): Transaction amount (positive = income, negative = expense)
            category (str): Transaction category
            description (str, optional): Transaction description

        Returns:
            Transaction: The newly created and saved transaction

        Raises:
            InvalidTransactionError: If transaction data is invalid
        """
        # Create transaction with validation (handled by Transaction constructor)
        transaction = Transaction(date, amount, category, description)

        # Add to account (includes ID assignment and storage)
        self.account.add_transaction(transaction)

        return transaction

    def get_monthly_spending(self, year=None, month=None):
        """
        Calculate total spending for a specific month.

        This method calculates the total amount spent (expenses) in a given month.
        Only transactions with negative amounts (expenses) are included.
        The absolute value is used to provide positive spending totals.

        Args:
            year (int, optional): Year for calculation (defaults to current year)
            month (int, optional): Month for calculation (defaults to current month)

        Returns:
            float: Total spending amount for the specified month
        """
        # Use current date if no specific month provided
        if year is None or month is None:
            today = datetime.date.today()
            year, month = today.year, today.month

        # Calculate start and end dates for the target month
        start_month = datetime.date(year, month, 1)  # First day of month
        if month == 12:
            end_month = datetime.date(year + 1, 1, 1)  # First day of next year
        else:
            end_month = datetime.date(year, month + 1, 1)  # First day of next month

        # Get all transactions for the specified month
        monthly_transactions = self.account.list_transactions(
            start_date=start_month,
            end_date=end_month
        )

        # Calculate total spending (sum of absolute values of negative transactions)
        return sum(abs(t.amount) for t in monthly_transactions if t.amount < 0)

    def get_monthly_income(self, year=None, month=None):
        """
        Calculate total income for a specific month.

        This method calculates the total income received in a given month.
        Only transactions with positive amounts (income) are included.

        Args:
            year (int, optional): Year for calculation (defaults to current year)
            month (int, optional): Month for calculation (defaults to current month)

        Returns:
            float: Total income amount for the specified month
        """
        # Use current date if no specific month provided
        if year is None or month is None:
            today = datetime.date.today()
            year, month = today.year, today.month

        # Calculate start and end dates for the target month
        start_month = datetime.date(year, month, 1)
        if month == 12:
            end_month = datetime.date(year + 1, 1, 1)
        else:
            end_month = datetime.date(year, month + 1, 1)

        # Get all transactions for the specified month
        monthly_transactions = self.account.list_transactions(
            start_date=start_month,
            end_date=end_month
        )

        # Calculate total income (sum of positive transactions)
        return sum(t.amount for t in monthly_transactions if t.amount > 0)

    def get_category_totals(self, year=None, month=None):
        """
        Get spending totals by category for a specific month.

        This method provides detailed breakdown of spending by category,
        useful for charts and budget analysis. It includes both income
        and expenses by category.

        Args:
            year (int, optional): Year for calculation (defaults to current year)
            month (int, optional): Month for calculation (defaults to current month)

        Returns:
            dict: Dictionary mapping category names to total amounts
        """
        # Use current date if no specific month provided
        if year is None or month is None:
            today = datetime.date.today()
            year, month = today.year, today.month

        # Calculate start and end dates for the target month
        start_month = datetime.date(year, month, 1)
        if month == 12:
            end_month = datetime.date(year + 1, 1, 1)
        else:
            end_month = datetime.date(year, month + 1, 1)

        # Get all transactions for the specified month
        monthly_transactions = self.account.list_transactions(
            start_date=start_month,
            end_date=end_month
        )

        # Aggregate amounts by category
        category_totals = {}
        for t in monthly_transactions:
            category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

        return category_totals

    def get_category_spending(self, year=None, month=None):
        """
        Get spending amounts by category (positive values for pie chart).

        This method is specifically designed for chart visualization.
        It returns only expense categories with positive values (absolute)
        suitable for pie charts and other visualizations.

        Args:
            year (int, optional): Year for calculation (defaults to current year)
            month (int, optional): Month for calculation (defaults to current month)

        Returns:
            dict: Dictionary mapping category names to spending amounts (positive)
        """
        # Get category totals for the period
        category_totals = self.get_category_totals(year, month)

        # Filter to only expenses and convert to positive values for charts
        return {k: abs(v) for k, v in category_totals.items() if v < 0}

    def get_balance(self):
        """
        Get current account balance.

        This method provides the total account balance by summing
        all transaction amounts across the entire account history.

        Returns:
            float: Current account balance
        """
        return self.account.get_balance()

    def get_transaction_by_id(self, transaction_id):
        """
        Get a specific transaction by ID.

        Args:
            transaction_id (int): Unique transaction identifier

        Returns:
            Transaction or None: The transaction if found, None otherwise
        """
        return self.account.get_transaction_by_id(transaction_id)

    def update_transaction(self, transaction_id, **updates):
        """
        Update a transaction with new values.

        This method provides a flexible way to update transaction properties.
        Only the specified parameters are updated, others remain unchanged.

        Args:
            transaction_id (int): ID of transaction to update
            **updates: Keyword arguments for fields to update
                      (date, amount, category, description)
        """
        self.account.update_transaction(transaction_id, **updates)

    def delete_transaction(self, transaction_id):
        """
        Delete a transaction from the account.

        Args:
            transaction_id (int): ID of transaction to delete

        Returns:
            bool: True if deleted successfully, False if not found
        """
        return self.account.delete_transaction(transaction_id)

    def import_transactions_from_csv(self, csv_content):
        """
        Import multiple transactions from CSV content.

        This method processes CSV data in bulk, creating transactions
        for each valid row and collecting errors for invalid rows.
        It provides detailed feedback on import success/failure.

        Args:
            csv_content (str): CSV data as a string

        Returns:
            tuple: (imported_count, errors_list)
                - imported_count (int): Number of successfully imported transactions
                - errors_list (list): List of error messages for failed imports
        """
        # Import utility function for CSV parsing
        from utils import parse_csv_line

        # Split CSV content into individual lines
        lines = csv_content.strip().splitlines()
        imported = 0  # Counter for successful imports
        errors = []   # List to collect error messages

        # Process each line of the CSV
        for i, line in enumerate(lines):
            try:
                # Parse CSV line into transaction components
                date, amount, category, description = parse_csv_line(line)

                # Create transaction using service method
                self.create_transaction(date, amount, category, description)
                imported += 1

            except Exception as e:
                # Collect error information for this line
                errors.append(f"Line {i+1}: {e}")

        return imported, errors

    def get_budget_status(self, category):
        """
        Get budget status for a specific category.

        This method provides budget tracking information by comparing
        the set budget against actual spending in that category.

        Args:
            category (str): Budget category to check

        Returns:
            dict or None: Budget status information, or None if no budget set
                - budget (float): Budget amount
                - spent (float): Amount spent
                - remaining (float): Remaining budget
        """
        # Check if budget functionality is available
        if not self.budget:
            return None

        # Calculate spending in this category for current month
        spent = abs(self.get_category_totals().get(category, 0))

        # Get budget amount for this category
        budget_amount = self.budget.get_budget(category)

        # Calculate remaining budget
        remaining = budget_amount - spent

        return {
            'budget': budget_amount,    # Total budget for category
            'spent': spent,             # Amount already spent
            'remaining': remaining      # Budget remaining
        }
