#!/usr/bin/python3.7

from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

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
	status = db.Column(db.Integer, default=1)
	note = db.Column(db.Text, nullable=False)
	location = db.Column(db.String(255), nullable=False)
	last_updated = db.Column(db.DateTime, default=datetime.utcnow)


db.create_all()

# Add users here to be inserted by default
users = [
	{'username': 'jnunn', 'password': 'password', 'name': 'Jeremy N', 'active': True},
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
	{'type': 'Truck', 'tracking_code': "AA123", "note": "Added truck #AA123 into tracking system", "location": "VIC"},
	{'type': 'Container', 'tracking_code': "HS333", "note": "Added Container into tracking system", "location": "SA"},
	{'type': 'Ship', 'tracking_code': "AA231", "note": "Added Ship into tracking system", "location": "QLD"},
	{'type': 'Computer', 'tracking_code': "AE048", "note": "Added Computer into tracking system", "location": "VIC"},
	{'type': 'Documents', 'tracking_code': "HD084", "note": "Added Documents into tracking system", "location": "QLD"},
	{'type': 'Car', 'tracking_code': "EF049", "note": "Added Car into tracking system", "location": "VIC"},
]

for a in assets:
	asset = Assets(type = a.get('type'), tracking_code = a.get('tracking_code'))
	assetstatus = AssetStatus(ass_id = a.get('tracking_code'), note = a.get('note'), location = a.get('location'))
	db.session.add(asset)
	db.session.add(assetstatus)
	db.session.commit()