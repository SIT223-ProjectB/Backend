#!/usr/bin/python3.7

from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from __init__ import db, app

# Users Table
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(120), nullable=False)
	name = db.Column(db.String(120), nullable=False)
	active = db.Column(db.Boolean, default=False)

	# Hash users password and verify them using sha256_crypt
	def hash_password(self, password):
		self.password = pwd_context.hash(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password)

	# JWT Authentication for API
	def generate_auth_token(self, expiration=3600):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		user = User.query.get(data['id'])
		return user 

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
