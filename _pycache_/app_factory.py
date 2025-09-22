from flask import Flask
from models import Account, Budget
from services.transaction_service import TransactionService
from repositories.transaction_repository import TransactionRepository
from config.app_config import AppConfig

class AppFactory:
    """Factory class for creating application components"""

    @staticmethod
    def create_app():
        """Create and configure the Flask application"""
        app = Flask(
            __name__,
            template_folder=AppConfig.TEMPLATE_FOLDER,
            static_folder=AppConfig.STATIC_FOLDER
        )
        app.config.from_object(AppConfig)
        return app

    @staticmethod
    def create_account():
        """Create an account instance"""
        return Account()

    @staticmethod
    def create_budget():
        """Create a budget instance"""
        return Budget()

    @staticmethod
    def create_transaction_service(account, budget=None):
        """Create a transaction service instance"""
        return TransactionService(account, budget)

    @staticmethod
    def create_transaction_repository(account):
        """Create a transaction repository instance"""
        return TransactionRepository(account)

    @staticmethod
    def create_full_app():
        """Create a complete application with all components"""
        app = AppFactory.create_app()
        account = AppFactory.create_account()
        budget = AppFactory.create_budget()
        transaction_service = AppFactory.create_transaction_service(account, budget)
        repository = AppFactory.create_transaction_repository(account)

        return {
            'app': app,
            'account': account,
            'budget': budget,
            'transaction_service': transaction_service,
            'repository': repository
        }
