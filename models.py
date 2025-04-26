from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    location = db.Column(db.String)
    image_url = db.Column(db.String)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    barcode = db.Column(db.String)
    name = db.Column(db.String)
    action = db.Column(db.String)
    quantity = db.Column(db.Integer)
    purpose = db.Column(db.String)  # Optional: for OUT or REQUEST
    task = db.Column(db.String)     # Optional: where/how it will be used

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    barcode = db.Column(db.String)
    name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    purpose = db.Column(db.String)
    task = db.Column(db.String)
    requested_by = db.Column(db.String)
