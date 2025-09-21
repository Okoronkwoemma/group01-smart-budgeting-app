"""
Smart Budgeting App - Main Flask Application

This module serves as the main entry point for the Smart Budgeting web application.
It implements a Flask web server with comprehensive transaction management capabilities
including CRUD operations, CSV import, dashboard analytics, and REST API endpoints.

The application follows a clean architecture pattern using:
- Factory pattern for dependency injection
- Service layer for business logic
- Repository pattern for data access
- Template-based UI with Bootstrap styling

Key Features:
- Transaction management (Create, Read, Update, Delete)
- Dashboard with financial overview and charts
- CSV import functionality for bulk transactions
- REST API for external integrations
- Responsive web interface

Author: Smart Budgeting Team
Version: 2.0.0
"""

# ============================================================================
# IMPORTS SECTION
# ============================================================================

# Standard library imports for core functionality
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Local application imports using factory pattern for clean architecture
from factories.app_factory import AppFactory  # Creates and configures all app components
from models import InvalidTransactionError    # Custom exception for transaction validation

# Standard library import for date/time operations
import datetime

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

"""
Initialize all application components using the Factory pattern.

This approach provides several benefits:
1. Centralized component creation and configuration
2. Easy testing with dependency injection
3. Clean separation of concerns
4. Consistent application setup across different environments

The factory creates:
- app: Flask application instance with proper configuration
- account: Account model for transaction storage
- budget: Budget model for financial planning
- transaction_service: Service layer for business logic
- repository: Data access layer for transactions
"""
components = AppFactory.create_full_app()
app = components['app']                    # Main Flask application instance
account = components['account']            # Account model for data storage
budget = components['budget']              # Budget model for financial planning
transaction_service = components['transaction_service']  # Business logic layer
repository = components['repository']      # Data access layer

# ============================================================================
# ROUTE HANDLERS
# ============================================================================

@app.route('/')
def dashboard():
    """
    Main dashboard route displaying financial overview and analytics.

    This endpoint serves as the application's home page, providing users with:
    - Current account balance
    - Monthly spending summary
    - Category-wise spending breakdown for charts
    - Quick access to transaction management

    The dashboard aggregates data from multiple sources:
    1. Transaction service for balance calculations
    2. Monthly spending analysis
    3. Category totals for visualization

    Returns:
        Rendered HTML template with financial data passed as context variables
        for display in charts and summary cards.
    """
    # Calculate total account balance across all transactions
    total_balance = transaction_service.get_balance()

    # Calculate spending for current month only
    monthly_spend = transaction_service.get_monthly_spending()

    # Get category breakdown for current month (used by charts)
    category_totals = transaction_service.get_category_totals()

    # Render dashboard template with calculated financial data
    return render_template(
        'dashboard.html',
        total_balance=total_balance,    # Current account balance
        monthly_spend=monthly_spend,    # Total spending this month
        category_totals=category_totals # Category breakdown for charts
    )

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    """
    Handle transaction listing and creation operations.

    This route serves dual purposes:
    1. GET: Display all transactions in a paginated table format
    2. POST: Process new transaction creation from form submission

    The route implements comprehensive error handling for:
    - Invalid date formats
    - Non-numeric amount values
    - Transaction validation errors
    - Missing required fields

    Form Data Expected (POST):
    - date: Transaction date in YYYY-MM-DD format
    - amount: Transaction amount (positive for income, negative for expenses)
    - category: Transaction category (e.g., "Food", "Transportation")
    - description: Optional transaction description

    Returns:
        GET: Rendered HTML template with transaction list
        POST: Redirect to transaction list on success, error message on failure
    """
    if request.method == 'POST':
        try:
            # Extract and validate form data
            date_str = request.form['date']                    # Date string from form
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()  # Parse to date object
            amount = float(request.form['amount'])             # Convert amount to float
            category = request.form['category']                # Transaction category
            description = request.form.get('description', '')  # Optional description

            # Create transaction using service layer (includes validation)
            transaction_service.create_transaction(date, amount, category, description)

            # Redirect to transaction list on successful creation
            return redirect(url_for('transactions'))

        except (ValueError, InvalidTransactionError) as e:
            # Handle validation errors with user-friendly messages
            return f"Error: {e}", 400

    # GET request: retrieve and display all transactions
    transactions = repository.find_all()  # Get all transactions from repository
    return render_template('transactions.html', transactions=transactions)

@app.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    """
    Handle transaction editing operations.

    This route allows users to modify existing transactions by:
    1. GET: Display transaction data in edit form
    2. POST: Process form submission and update transaction

    URL Parameter:
    - transaction_id: Integer ID of the transaction to edit

    The route includes comprehensive validation and error handling:
    - Transaction existence check
    - Date format validation
    - Amount validation
    - Category validation

    Returns:
        GET: Edit form populated with transaction data
        POST: Redirect to transaction list on success, error on failure
        404: If transaction doesn't exist
    """
    # Retrieve transaction by ID from repository
    transaction = repository.find_by_id(transaction_id)
    if not transaction:
        return "Transaction not found", 404  # Return 404 for non-existent transactions

    if request.method == 'POST':
        try:
            # Extract updated form data
            date_str = request.form['date']
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(request.form['amount'])
            category = request.form['category']
            description = request.form.get('description', '')

            # Update transaction using repository (includes validation)
            repository.update(
                transaction_id,
                date=date,          # New transaction date
                amount=amount,      # New transaction amount
                category=category,  # New transaction category
                description=description  # New transaction description
            )
            return redirect(url_for('transactions'))  # Redirect on successful update

        except (ValueError, InvalidTransactionError) as e:
            return f"Error: {e}", 400  # Handle validation errors

    # GET request: render edit form with current transaction data
    return render_template('edit_transaction.html', transaction=transaction)

@app.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
def delete_transaction(transaction_id):
    """
    Handle transaction deletion operations.

    This route permanently removes transactions from the system.
    Only accepts POST requests for security (prevents accidental deletion via GET).

    URL Parameter:
    - transaction_id: Integer ID of the transaction to delete

    Returns:
        Redirect to transaction list on success
        Error message if transaction not found
    """
    # Attempt to delete transaction (repository handles existence check)
    if repository.delete(transaction_id):
        return redirect(url_for('transactions'))  # Success: redirect to list
    else:
        return f"Error: Transaction not found", 404  # Transaction doesn't exist

@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    """
    Handle CSV file import functionality for bulk transaction creation.

    This route allows users to upload CSV files containing multiple transactions
    for batch processing. The system validates each row and provides detailed
    feedback on import success/failure.

    CSV Format Expected:
    - Column 1: Date (YYYY-MM-DD format)
    - Column 2: Amount (numeric value)
    - Column 3: Category (string)
    - Column 4: Description (optional string)

    Returns:
        GET: Import form for file upload
        POST: Import results page with success/error counts
    """
    if request.method == 'POST':
        # Process uploaded file
        file = request.files.get('file')
        if not file:
            return "No file uploaded", 400  # Handle missing file

        # Read and decode file content
        content = file.read().decode('utf-8')

        # Import transactions using service layer (handles validation and error collection)
        imported, errors = transaction_service.import_transactions_from_csv(content)

        # Display results with import summary
        return render_template('import_result.html', imported=imported, errors=errors)

    # GET request: show import form
    return render_template('import.html')

@app.route('/category_data')
def category_data():
    """
    Provide category spending data for dashboard charts.

    This API endpoint returns JSON data specifically formatted for
    frontend chart libraries (like Chart.js or D3.js) to display
    spending breakdowns by category.

    The data includes only expense categories (negative amounts)
    and converts them to positive values for display purposes.

    Returns:
        JSON object with category names as keys and spending amounts as values
    """
    data = transaction_service.get_category_spending()
    return jsonify(data)

@app.route('/api/transactions')
def api_transactions():
    """
    REST API endpoint for retrieving all transactions.

    This endpoint provides a JSON representation of all transactions
    in the system, suitable for external applications, mobile apps,
    or frontend JavaScript frameworks that need transaction data.

    Returns:
        JSON array of transaction objects with all transaction properties
    """
    transactions = repository.find_all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/balance')
def api_balance():
    """
    REST API endpoint for retrieving account balance and summary data.

    This endpoint provides key financial metrics in JSON format:
    - Current account balance
    - Monthly spending total
    - Monthly income total

    This data is commonly used by:
    - Dashboard widgets
    - Mobile applications
    - External financial tools
    - Reporting systems

    Returns:
        JSON object with balance, monthly_spend, and monthly_income
    """
    return jsonify({
        'balance': transaction_service.get_balance(),        # Total account balance
        'monthly_spend': transaction_service.get_monthly_spending(),  # Current month expenses
        'monthly_income': transaction_service.get_monthly_income()    # Current month income
    })

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Application entry point for development server.

    This block only executes when the script is run directly (not imported).
    It starts the Flask development server with debug mode enabled for
    development purposes.

    In production environments, this should be replaced with a WSGI server
    like Gunicorn or uWSGI for better performance and security.
    """
    app.run(debug=app.config['DEBUG'])
