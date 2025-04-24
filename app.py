from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

EXCEL_FILE = 'inventory.xlsx'

# Load or initialize Excel file
def load_inventory():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name=None)
    else:
        df = {
            'Inventory': pd.DataFrame(columns=['Barcode', 'Product Name', 'Quantity', 'Location', 'Image URL']),
            'Log': pd.DataFrame(columns=['Timestamp', 'Barcode', 'Product Name', 'Action', 'Quantity Changed']),
            'Requests': pd.DataFrame(columns=['Timestamp', 'Barcode', 'Product Name', 'Quantity', 'Purpose', 'Task', 'Requested By'])
        }
    return df

def save_inventory(data):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
        data['Inventory'].to_excel(writer, sheet_name='Inventory', index=False)
        data['Log'].to_excel(writer, sheet_name='Log', index=False)
        data['Requests'].to_excel(writer, sheet_name='Requests', index=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_inventory()
    inventory_df = data['Inventory']

    if request.method == 'POST':
        action = request.form.get('action')
        barcode = request.form.get('barcode', '').strip()
        quantity = int(request.form.get('quantity', 1))
        purpose = request.form.get('purpose', '')
        task = request.form.get('task', '')

        if barcode == '':
            flash("Please enter a barcode.", "warning")
            return redirect(url_for('index'))

        match = inventory_df[inventory_df['Barcode'] == barcode]

        if match.empty:
            flash("Barcode not found in inventory.", "danger")
        else:
            idx = match.index[0]
            product_name = inventory_df.loc[idx, 'Product Name']
            current_qty = inventory_df.loc[idx, 'Quantity']

            if action == 'IN':
                inventory_df.at[idx, 'Quantity'] += quantity
                log_action = True
            elif action == 'OUT':
                if current_qty >= quantity:
                    inventory_df.at[idx, 'Quantity'] -= quantity
                    log_action = True
                else:
                    flash("Not enough stock.", "danger")
                    return redirect(url_for('index'))
            elif action == 'REQUEST':
                new_request = pd.DataFrame([[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), barcode, product_name, quantity, purpose, task, session['user']]],
                                           columns=['Timestamp', 'Barcode', 'Product Name', 'Quantity', 'Purpose', 'Task', 'Requested By'])
                data['Requests'] = pd.concat([data['Requests'], new_request], ignore_index=True)
                log_action = False
                flash("Request submitted.", "info")

            if log_action:
                new_log = pd.DataFrame([[datetime.now().strftime('%Y-%m-%d %H:%M:%S'), barcode, product_name, action, quantity]],
                                       columns=['Timestamp', 'Barcode', 'Product Name', 'Action', 'Quantity Changed'])
                data['Log'] = pd.concat([data['Log'], new_log], ignore_index=True)
                flash(f"{action} successful for {product_name}.", "success")

            save_inventory(data)

        return redirect(url_for('index'))

    return render_template('index.html', user=session['user'], inventory=inventory_df.to_dict(orient='records'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple login logic (replace with DB later)
        if username == 'admin' and password == '1234':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash("Invalid login.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
