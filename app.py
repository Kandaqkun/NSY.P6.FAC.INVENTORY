from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import pandas as pd

from models import db, Inventory, Log, Request as RequestModel

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['REPORT_FOLDER'] = 'static/reports'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')
        barcode = request.form.get('barcode', '').strip()
        quantity = int(request.form.get('quantity', 1))
        purpose = request.form.get('purpose', '')
        task = request.form.get('task', '')
        file = request.files.get('image')

        if barcode == '':
            flash("Please enter a barcode.", "warning")
            return redirect(url_for('index'))

        product = Inventory.query.filter_by(barcode=barcode).first()

        if not product:
            flash("Barcode not found in inventory.", "danger")
        else:
            if action == 'IN':
                product.quantity += quantity
                flash(f"IN success for {product.name}.", "success")
                db.session.add(Log(timestamp=datetime.now(), barcode=barcode, name=product.name, action='IN', quantity=quantity))

            elif action == 'OUT':
                if product.quantity >= quantity:
                    product.quantity -= quantity
                    flash(f"OUT success for {product.name}.", "success")
                    db.session.add(Log(timestamp=datetime.now(), barcode=barcode, name=product.name, action='OUT', quantity=quantity))
                else:
                    flash("Not enough stock.", "danger")
                    return redirect(url_for('index'))

            elif action == 'REQUEST':
                flash("Request submitted.", "info")
                db.session.add(RequestModel(timestamp=datetime.now(), barcode=barcode, name=product.name, quantity=quantity, purpose=purpose, task=task, requested_by=session['user']))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                product.image_url = f"/static/uploads/{filename}"

            db.session.commit()

        return redirect(url_for('index'))

    inventory = Inventory.query.all()
    return render_template('index.html', user=session['user'], inventory=inventory)

@app.route('/report')
def generate_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    logs = Log.query.all()
    data = [{
        'Timestamp': log.timestamp,
        'Barcode': log.barcode,
        'Product Name': log.name,
        'Action': log.action,
        'Quantity': log.quantity
    } for log in logs]

    df = pd.DataFrame(data)
    filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(app.config['REPORT_FOLDER'], filename)
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)

@app.route('/logs')
def logs():
    if 'user' not in session:
        return redirect(url_for('login'))

    filter_barcode = request.args.get('barcode')
    filter_action = request.args.get('action')

    query = Log.query
    if filter_barcode:
        query = query.filter_by(barcode=filter_barcode)
    if filter_action:
        query = query.filter_by(action=filter_action)

    logs = query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
