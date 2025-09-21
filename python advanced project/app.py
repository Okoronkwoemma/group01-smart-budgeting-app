from flask import Flask, render_template, request, redirect, url_for, jsonify
from factories.app_factory import AppFactory
from models import InvalidTransactionError
import datetime

# Create application components using Factory pattern
components = AppFactory.create_full_app()
app = components['app']
account = components['account']
budget = components['budget']
transaction_service = components['transaction_service']
repository = components['repository']

@app.route('/')
def dashboard():
    """Dashboard showing balance, spending, and category breakdown"""
    total_balance = transaction_service.get_balance()
    monthly_spend = transaction_service.get_monthly_spending()
    category_totals = transaction_service.get_category_totals()

    return render_template(
        'dashboard.html',
        total_balance=total_balance,
        monthly_spend=monthly_spend,
        category_totals=category_totals
    )

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    """Handle transaction listing and creation"""
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(request.form['amount'])
            category = request.form['category']
            description = request.form.get('description', '')

            transaction_service.create_transaction(date, amount, category, description)
            return redirect(url_for('transactions'))
        except (ValueError, InvalidTransactionError) as e:
            return f"Error: {e}", 400

    transactions = repository.find_all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    """Handle transaction editing"""
    transaction = repository.find_by_id(transaction_id)
    if not transaction:
        return "Transaction not found", 404

    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(request.form['amount'])
            category = request.form['category']
            description = request.form.get('description', '')

            repository.update(
                transaction_id,
                date=date,
                amount=amount,
                category=category,
                description=description
            )
            return redirect(url_for('transactions'))
        except (ValueError, InvalidTransactionError) as e:
            return f"Error: {e}", 400

    return render_template('edit_transaction.html', transaction=transaction)

@app.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
def delete_transaction(transaction_id):
    """Handle transaction deletion"""
    if repository.delete(transaction_id):
        return redirect(url_for('transactions'))
    else:
        return f"Error: Transaction not found", 404

@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    """Handle CSV import functionality"""
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return "No file uploaded", 400

        content = file.read().decode('utf-8')
        imported, errors = transaction_service.import_transactions_from_csv(content)

        return render_template('import_result.html', imported=imported, errors=errors)

    return render_template('import.html')

@app.route('/category_data')
def category_data():
    """Provide category spending data for charts"""
    data = transaction_service.get_category_spending()
    return jsonify(data)

@app.route('/api/transactions')
def api_transactions():
    """API endpoint for transaction data"""
    transactions = repository.find_all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/balance')
def api_balance():
    """API endpoint for balance data"""
    return jsonify({
        'balance': transaction_service.get_balance(),
        'monthly_spend': transaction_service.get_monthly_spending(),
        'monthly_income': transaction_service.get_monthly_income()
    })

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
