import sqlite3
import pandas as pd
from datetime import datetime
import os

# Detect path
if 'streamlit' in os.environ.get('HOME', ''):
    DB_PATH = os.path.join('/tmp', 'expenses.db')
else:
    DB_PATH = 'expenses.db'

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# ---------------------- User Table ----------------------

def create_user_table():
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            gender TEXT,
            secret TEXT,
            budget_limit REAL DEFAULT 0
        )
    ''')
    conn.commit()

def add_user(name, email, password, gender, secret):
    # Check if the email already exists in the database
    existing_user = get_user_by_email(email)
    if existing_user:
        raise ValueError("Email already exists.")
    
    # Insert the new user into the database if the email does not exist
    c.execute(''' 
        INSERT INTO users (name, email, password, gender, secret) 
        VALUES (?, ?, ?, ?, ?) 
    ''', (name, email, password, gender, secret))
    conn.commit()


def login_user(email, password):
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    return c.fetchone()

def get_user_by_email(email):
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    return c.fetchone()

def reset_password(email, secret, new_password):
    c.execute('''
        UPDATE users SET password = ?
        WHERE email = ? AND secret = ?
    ''', (new_password, email, secret))
    conn.commit()
    return c.rowcount > 0

# Delete User
def delete_user(email, secret):
    c.execute("DELETE FROM users WHERE email = ? AND secret = ?", (email, secret))
    conn.commit()
    return c.rowcount > 0


# ---------------------- Budget Limit ----------------------

def set_budget_limit(user_id, limit):
    c.execute('''
        UPDATE users SET budget_limit = ?
        WHERE id = ?
    ''', (limit, user_id))
    conn.commit()

def get_budget_limit(user_id):
    c.execute('SELECT budget_limit FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    return result[0] if result else 0

# ---------------------- Expense Table ----------------------

def create_expense_table():
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            "date" TEXT,
            category TEXT,
            amount REAL,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()

def insert_expense(user_id, date, category, amount, description):
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
        INSERT INTO expenses (user_id, "date", category, amount, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, date, category, amount, description))
    conn.commit()

def fetch_all_expenses(user_id):
    c.execute('''
        SELECT id, "date", category, amount, description
        FROM expenses WHERE user_id = ? ORDER BY "date" DESC
    ''', (user_id,))
    return c.fetchall()

def filter_by_category(user_id, category):
    c.execute('''
        SELECT id, "date", category, amount, description
        FROM expenses WHERE user_id = ? AND category = ? ORDER BY "date" DESC
    ''', (user_id, category))
    return c.fetchall()

def fetch_by_month(user_id, month):
    c.execute('''
        SELECT SUM(amount) FROM expenses
        WHERE user_id = ? AND strftime('%m', "date") = ?
    ''', (user_id, f"{int(month):02}"))
    res = c.fetchone()[0]
    return res if res else 0.0

def fetch_by_year(user_id, year):
    c.execute('''
        SELECT SUM(amount) FROM expenses
        WHERE user_id = ? AND strftime('%Y', "date") = ?
    ''', (user_id, str(year)))
    res = c.fetchone()[0]
    return res if res else 0.0

def fetch_category_summary(user_id):
    c.execute('''
        SELECT category, SUM(amount)
        FROM expenses WHERE user_id = ?
        GROUP BY category
    ''', (user_id,))
    data = c.fetchall()
    return pd.DataFrame(data, columns=["Category", "Total"])

def fetch_monthly_summary(user_id):
    c.execute('''
        SELECT strftime('%m', "date") as month, SUM(amount)
        FROM expenses WHERE user_id = ?
        GROUP BY month ORDER BY month
    ''', (user_id,))
    data = c.fetchall()
    return pd.DataFrame(data, columns=["Month", "Total"])

def delete_expense_by_id(expense_id):
    c.execute('''
        DELETE FROM expenses WHERE id = ?
    ''', (expense_id,))
    conn.commit()

def update_expense_by_id(expense_id, date=None, category=None, amount=None, description=None):
    query = "UPDATE expenses SET "
    values = []
    
    if date:
        query += '"date" = ?, '
        values.append(date)
    if category:
        query += 'category = ?, '
        values.append(category)
    if amount:
        query += 'amount = ?, '
        values.append(amount)
    if description:
        query += 'description = ?, '
        values.append(description)
    
    query = query.rstrip(', ') + " WHERE id = ?"
    values.append(expense_id)
    
    c.execute(query, tuple(values))
    conn.commit()
