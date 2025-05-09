from database.database import (
    delete_expense_by_id, insert_expense, fetch_all_expenses, filter_by_category,
    fetch_by_month, fetch_by_year, fetch_category_summary, fetch_monthly_summary,
    add_user, login_user, get_user_by_email, reset_password,
    set_budget_limit, get_budget_limit, update_expense_by_id
)

# ---------------------- User Auth ----------------------
def register_user(name, email, password, gender, secret):
    add_user(name, email, password, gender, secret)

def authenticate_user(email, password):
    return login_user(email, password)

def recover_user(email):
    return get_user_by_email(email)

def update_user_password(email, secret, new_password):
    return reset_password(email, secret, new_password)

# ---------------------- Budget Limit ----------------------
def set_user_budget(user_id, limit):
    return set_budget_limit(user_id, limit)

def get_user_budget(user_id):
    return get_budget_limit(user_id)

# ---------------------- Expense ----------------------
def add_expense(user_id, date, category, amount, description):
    insert_expense(user_id, date, category, amount, description)

def get_expenses(user_id):
    return fetch_all_expenses(user_id)

def filter_expenses_by_category(user_id, category):
    return filter_by_category(user_id, category)

def get_total_by_month(user_id, month):
    return fetch_by_month(user_id, month)

def get_total_by_year(user_id, year):
    return fetch_by_year(user_id, year)

def get_category_summary(user_id):
    return fetch_category_summary(user_id)

def get_monthly_summary(user_id):
    return fetch_monthly_summary(user_id)

# ---------------------- Expense Edit/Delete ----------------------
def delete_expense(expense_id):
    return delete_expense_by_id(expense_id)

def update_expense(expense_id, date=None, category=None, amount=None, description=None):
    return update_expense_by_id(expense_id, date, category, amount, description)