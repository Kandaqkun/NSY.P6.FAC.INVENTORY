from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    image_url = db.Column(db.String(255))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    barcode = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    barcode = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(255))
    task = db.Column(db.String(255))
    requested_by = db.Column(db.String(100), nullable=False)
