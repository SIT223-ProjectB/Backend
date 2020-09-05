#!/usr/bin/python3.7

from flask import Blueprint, jsonify, abort, request, g
from flask_httpauth import HTTPBasicAuth

from db import User, db

api = Blueprint('api', __name__)
auth = HTTPBasicAuth()

#
# Password Verification
# 
@auth.verify_password
def _verify_password(username_or_tok, password):
	# Try to verify based on auth token
	user = User.verify_auth_token(username_or_tok)
	if not user:
		# Get the user object
		user = User.query.filter_by(username = username_or_tok).first()
		# if its invalid or passord is wrong
		if not user or not user.verify_password(password):
			return False
	g.user = user
	return True

# Creation of a new user
@api.route('/users/create', methods=['POST'])
def create_new_user():
	try:
		username = request.json.get('username')
		password = request.json.get('password')
		name = request.json.get('name')
	except:
		abort(400, "Missing Arguments")
	if username is None or password is None or name is None:
		abort(400, "Missing Arguments")
	if User.query.filter_by(username = username).first() is not None:
		abort(400, "Username Taken!")
	# Create new user object
	user = User(username = username, name = name)
	user.hash_password(password)
	# add user to the database
	db.session.add(user)
	db.session.commit()
	return jsonify({'username': user.username})


# Token Authentication
@api.route('/token')
@auth.login_required
def create_auth_token():
	token = g.user.generate_auth_token()
	return jsonify({'success': 1, 'token': token.decode('ascii')})

# Mock resource thats locked behind auth
@api.route('/resource')
@auth.login_required
def protected():
	return jsonify({'success': 1, 'msg': 'private resource'})
