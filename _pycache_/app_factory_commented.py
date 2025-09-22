"""
Smart Budgeting App - Application Factory Pattern

This module implements the Factory pattern for creating and configuring
all application components. It provides centralized component creation,
dependency injection, and consistent application setup across different
environments.

The Factory pattern provides several key benefits:
- Centralized component creation and configuration
- Easy testing with dependency injection
- Clean separation of concerns
- Consistent application setup
- Simplified main application file
- Environment-specific configuration

Key Features:
- Flask application creation with proper configuration
- Component dependency injection
- Clean architecture support
- Test-friendly design
- Configuration management

Author: Smart Budgeting Team
Version: 2.0.0
"""

# Flask framework import for web application creation
from flask import Flask

# Local application imports for all core components
from models import Account, Budget                          # Domain models
from services.transaction_service import TransactionService  # Business logic layer
from repositories.transaction_repository import TransactionRepository  # Data access layer
from config.app_config import AppConfig                    # Application configuration

# ============================================================================
# APPLICATION FACTORY CLASS
# ============================================================================

class AppFactory:
    """
    Factory class for creating and configuring application components.

    This class implements the Factory pattern to provide centralized
    creation and configuration of all application components. It ensures
    consistent setup and makes dependency injection easy for testing.

    Key Responsibilities:
    - Flask application creation and configuration
    - Component creation with proper dependencies
    - Dependency injection for testability
    - Configuration management
    - Clean architecture support

    The factory provides both individual component creation methods
    and a convenience method for creating a complete application setup.
    """

    @staticmethod
    def create_app():
        """
        Create and configure the Flask application instance.

        This method creates a properly configured Flask application with:
        - Template and static folder configuration
        - Application settings from AppConfig
        - Debug and testing configuration
        - Extension initialization (if needed)

        Returns:
            Flask: Configured Flask application instance

        Configuration Applied:
        - Template folder path from AppConfig
        - Static folder path from AppConfig
        - All settings from AppConfig class
        - Debug mode settings
        - Testing configuration
        """
        # Create Flask app with custom template and static folders
        app = Flask(
            __name__,
            template_folder=AppConfig.TEMPLATE_FOLDER,  # Custom template directory
            static_folder=AppConfig.STATIC_FOLDER      # Custom static files directory
        )

        # Apply configuration from AppConfig class
        app.config.from_object(AppConfig)

        return app

    @staticmethod
    def create_account():
        """
        Create a new Account instance for transaction storage.

        This method creates a fresh Account instance ready to store
        and manage financial transactions. The account starts empty
        and will automatically assign IDs to new transactions.

        Returns:
            Account: New account instance with empty transaction list
        """
        return Account()

    @staticmethod
    def create_budget():
        """
        Create a new Budget instance for financial planning.

        This method creates a fresh Budget instance for managing
        category-based budget limits and tracking. The budget starts
        empty and budgets can be set for different categories.

        Returns:
            Budget: New budget instance with empty budget collection
        """
        return Budget()

    @staticmethod
    def create_transaction_service(account, budget=None):
        """
        Create a TransactionService instance with required dependencies.

        This method creates a service layer instance that coordinates
        between the account, budget, and provides high-level business
        operations for transaction management.

        Args:
            account (Account): Account instance for transaction operations
            budget (Budget, optional): Budget instance for budget tracking

        Returns:
            TransactionService: Configured service instance
        """
        return TransactionService(account, budget)

    @staticmethod
    def create_transaction_repository(account):
        """
        Create a TransactionRepository instance with required dependencies.

        This method creates a data access layer instance that provides
        a clean interface for transaction data operations. The repository
        abstracts the underlying data storage mechanism.

        Args:
            account (Account): Account instance for data storage

        Returns:
            TransactionRepository: Configured repository instance
        """
        return TransactionRepository(account)

    @staticmethod
    def create_full_app():
        """
        Create a complete application with all components configured.

        This convenience method creates a fully configured application
        with all components properly wired together. It's the main entry
        point for application initialization and provides a clean way
        to get all components with their dependencies properly set up.

        Returns:
            dict: Dictionary containing all application components:
                - 'app': Flask application instance
                - 'account': Account instance for data storage
                - 'budget': Budget instance for financial planning
                - 'transaction_service': Service layer for business logic
                - 'repository': Data access layer for transactions

        Usage Example:
            components = AppFactory.create_full_app()
            app = components['app']
            transaction_service = components['transaction_service']
            repository = components['repository']
        """
        # Create base application instance
        app = AppFactory.create_app()

        # Create domain model instances
        account = AppFactory.create_account()  # Transaction storage
        budget = AppFactory.create_budget()    # Budget planning

        # Create service layer with dependencies
        transaction_service = AppFactory.create_transaction_service(
            account,    # Account for transaction operations
            budget      # Budget for financial planning
        )

        # Create data access layer with dependencies
        repository = AppFactory.create_transaction_repository(
            account     # Account for data storage
        )

        # Return all components in a structured dictionary
        return {
            'app': app,                    # Main Flask application
            'account': account,            # Domain model for transactions
            'budget': budget,              # Domain model for budgets
            'transaction_service': transaction_service,  # Business logic layer
            'repository': repository       # Data access layer
        }
