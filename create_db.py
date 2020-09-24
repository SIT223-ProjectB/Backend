#!/usr/bin/python3.7

from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context 
from history_meta import (
Versioned, 
versioned_session
)

from config import current_config

app = Flask(__name__)
app.config.from_object(current_config)


db = SQLAlchemy(app)

# Users Table
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(120), nullable=False)
	name = db.Column(db.String(120), nullable=False)
	active = db.Column(db.Boolean, default=False)

	def hash_password(self, password):
		self.password = pwd_context.hash(password)

# Asset Table
class Assets(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(50), nullable=False)
	tracking_code = db.Column(db.String(20), nullable=False, unique=True)
	time_created = db.Column(db.DateTime, default=datetime.utcnow)
	status = db.relationship('AssetStatus', backref="asset", lazy=True)

# Asset Status
class AssetStatus(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ass_id = db.Column(db.String(20), db.ForeignKey('assets.tracking_code'), unique=True, nullable=False)
	status = db.Column(db.String(255), nullable=False)
	note = db.Column(db.Text, nullable=False)
	location = db.Column(db.String(255), nullable=False)
	def_location = db.Column(db.String(255), nullable=False)
	last_updated = db.Column(db.DateTime, default=datetime.utcnow)


# Asset Status Logs
# Stores changes to items, empty by default, populated automatically upon an item being modified or deleted
class AssetStatusLog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(50), nullable=False)
	ass_id = db.Column(db.String(20), db.ForeignKey('assets.tracking_code'), nullable=False)
	status = db.Column(db.String(255), nullable=False)
	note = db.Column(db.Text, nullable=False)
	location = db.Column(db.String(255), nullable=False)
	def_location = db.Column(db.String(255), nullable=False)
	#version = db.Column(db.Integer, default=0)
	timestamp = db.Column(db.DateTime,default=datetime.utcnow, nullable=False)


db.create_all()

# Add users here to be inserted by default
users = [
	{'username': 'jnunn', 'password': 'password', 'name': 'Jeremy N', 'active': True},
	{'username': 'anorwood', 'password': 'password', 'name': 'Aaron N', 'active': True},
	{'username': 'dev', 'password': 'password', 'name': 'Developer Account', 'active': False}
]

for u in users:
	user = User(username = u.get('username'), name = u.get('name'))
	user.hash_password(u.get('password'))
	user.active = u.get('active')
	db.session.add(user)
	db.session.commit()


# Dummy Assets
assets = [
	{'type': 'Truck',     'tracking_code': "AA123", "status": "available", "note": "Awaiting deployment",                       "location": "VIC", "def_location": "SA"},
	{'type': 'Container', 'tracking_code': "HS333", "status": "moved",     "note": "In transit to SA warehouse",                "location": "SA",  "def_location": "WA"},
	{'type': 'Ship',      'tracking_code': "CA231", "status": "available", "note": "Idle awaiting delivery",                   "location": "QLD", "def_location": "VIC"},
	{'type': 'Forklift',  'tracking_code': "KL384", "status": "moved",     "note": "Replacing QLD forklift pending delivery",   "location": "NT",  "def_location": "QLD"},
	{'type': 'Computer',  'tracking_code': "XE048", "status": "faulty",    "note": "Computer awaiting repairs ticket #A338",   "location": "VIC", "def_location": "VIC"},
	{'type': 'Documents', 'tracking_code': "HD084", "status": "lost",      "note": "Documents reported lost to management",     "location": "QLD", "def_location": "QLD"},
	{'type': 'Car',       'tracking_code': "EF049", "status": "available", "note": "Idle assignable to staff as needed",       "location": "VIC", "def_location": "NT"},
	{'type': 'Truck',     'tracking_code': "BA124", "status": "faulty",    "note": "Awaiting new components ticket #C322",     "location": "NT",  "def_location": "QLD"},
	{'type': 'Truck',     'tracking_code': "CH421", "status": "moved",     "note": "In transit transferred to NT warehouse",   "location": "NT",  "def_location": "QLD"},
	{'type': 'Car',       'tracking_code': "TA323", "status": "available", "note": "To be assigned to new NT warehouse manager","location": "VIC", "def_location": "NT"},
	{'type': 'Container', 'tracking_code': "MN129", "status": "available", "note": "Awaiting loading",                          "location": "WA",  "def_location": "WA"},
	{'type': 'Computer',  'tracking_code': "GF903", "status": "available", "note": "Awaiting transfer to new NT warehouse",     "location": "VIC", "def_location": "NT"},
	{'type': 'Documents', 'tracking_code': "AS564", "status": "moved",     "note": "Awaiting transfer to new NT warehouse",     "location": "VIC", "def_location": "QLD"},
	{'type': 'Forklift',  'tracking_code': "FL583", "status": "faulty",    "note": "Possible decomission pending sign-off",     "location": "QLD", "def_location": "QLD"},
	{'type': 'Crane',     'tracking_code': "ZJ652", "status": "available", "note": "Pending deployment",                        "location": "SA",  "def_location": "SA"},
	{'type': 'Car',       'tracking_code': "TA023", "status": "moved",     "note": "On loan to new NT warehouse",               "location": "NT",  "def_location": "QLD"},
	{'type': 'Forklift',  'tracking_code': "PO480", "status": "lost",      "note": "Could be behind the curtains",              "location": "SA",  "def_location": "SA"},
	{'type': 'Computer',  'tracking_code': "MS123", "status": "available", "note": "In use",                                    "location": "WA",  "def_location": "WA"},
	{'type': 'Documents', 'tracking_code': "AH943", "status": "available", "note": "Archived",                                  "location": "WA",  "def_location": "WA"},
	{'type': 'Forklift',  'tracking_code': "JK093", "status": "available", "note": "Idle awaiting deployment",                 "location": "SA",  "def_location": "VIC"},
]

for a in assets:
	asset = Assets(type = a.get('type'), tracking_code = a.get('tracking_code'))
	#added def_location and note
	assetstatus = AssetStatus(ass_id = a.get('tracking_code'), note = a.get('note'), location = a.get('location'), def_location = a.get('def_location'), status = a.get('status'))
	db.session.add(asset)
	db.session.add(assetstatus)
	db.session.commit()
