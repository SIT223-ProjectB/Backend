#!/usr/bin/python3.7

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from __init__ import db, app


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
