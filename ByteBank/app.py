from flask import Flask, render_template, request, redirect, url_for
from collections import defaultdict
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace
app.config['MYSQL_PASSWORD'] = 'bunny123'  # Replace
app.config['MYSQL_DB'] = 'bytebank'

mysql = MySQL(app)
def load_expenses():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    columns = [column[0] for column in cursor.description]
    expenses = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return expenses


def save_expense(new_expense):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (%s, %s, %s, %s)",
        (new_expense['date'], new_expense['category'], new_expense['amount'], new_expense['description'])
    )
    mysql.connection.commit()
    cursor.close()

def update_expense(expense_id, updated_expense):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE expenses SET date=%s, category=%s, amount=%s, description=%s WHERE id=%s",
        (updated_expense['date'], updated_expense['category'], updated_expense['amount'], updated_expense['description'], expense_id)
    )
    mysql.connection.commit()
    cursor.close()

def delete_expense(expense_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
    mysql.connection.commit()
    cursor.close()

def get_category_summary(expenses):
    summary = defaultdict(float)
    for exp in expenses:
        summary[exp['category']] += exp['amount']
    return dict(summary)

@app.route('/')
def index():
    expenses = load_expenses()
    total = sum(exp['amount'] for exp in expenses)
    category_summary = get_category_summary(expenses)
    filter_cat = request.args.get('filter_cat')
    filter_expenses = expenses
    if filter_cat:
        filter_expenses = [e for e in expenses if e['category'].lower() == filter_cat.lower()]
    return render_template('index.html', expenses=filter_expenses, total=total,
                           category_summary=category_summary, filter_cat=filter_cat, categories=list(category_summary.keys()))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_expense = {
            "date": request.form['date'],
            "category": request.form['category'],
            "amount": float(request.form['amount']),
            "description": request.form['description']
        }
        save_expense(new_expense)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit(expense_id):
    if request.method == 'POST':
        updated_expense = {
            "date": request.form['date'],
            "category": request.form['category'],
            "amount": float(request.form['amount']),
            "description": request.form['description']
        }
        update_expense(expense_id, updated_expense)
        return redirect(url_for('index'))
    else:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM expenses WHERE id=%s", (expense_id,))
        expense = cursor.fetchone()
        cursor.close()
        return render_template('edit.html', expense=expense)

@app.route('/delete/<int:expense_id>')
def delete(expense_id):
    delete_expense(expense_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
