#!/usr/bin/python3.7

from datetime import datetime
from flask import Blueprint, jsonify, abort, request, g, redirect, session, url_for
from flask_httpauth import HTTPBasicAuth

from filter import entity_encode
from db import db, User, Assets, AssetStatus, AssetStatusLog

api = Blueprint('api', __name__)
auth = HTTPBasicAuth()

#
# Password Verification
# 
@auth.verify_password
def _verify_password(username_or_tok, password):
	user = None
	# Try to verify based on session
	uid = session.get('user')
	if uid:
		user = User.query.filter_by(id=int(uid), active=True).first()
	if not user:
		# Try to verify based on auth token
		user = User.verify_auth_token(username_or_tok)
		if not user:
			# Get the user object
			user = User.query.filter_by(username = username_or_tok, active=True).first()
			# if its invalid or passord is wrong
			if not user or not user.verify_password(password):
				return False
	g.user = user
	return True

#
# Login User
#
@api.route('/login', methods=['GET'])
def login_user():
	try:
		# Check if user supplied their auth token
		if not request.args.get('token'):
			return redirect(url_for('ui.ui_login'))
		# Check if user is valid
		user = User.verify_auth_token(request.args.get('token'))
		if not user:
			return redirect(url_for('ui.ui_login'))
		# Clear and create a new session
		session.clear()
		session['user'] = user.id
		# Successful Auth
		return redirect(url_for('ui.ui_index'))
	except Exception as e:
		print(e)
		abort(401, "Not Authorized")
#
# Logout User
#
@api.route('/logout', methods=['GET'])
def logout_user():
	session.clear()
	return redirect(url_for('ui.ui_login'))

# Creation of a new user
#
# POST /api/users/create
# Content-Type: application/json
# 
# {"username": "jnunn", "password": "password", "name": "Jeremy N"}
#
##
@api.route('/users/create_new_user', methods=['POST'])
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

#
# Checks for valid usernames
#
@api.route('/users/check', methods=['GET'])
@auth.login_required
def check_user():
	try:
		username = request.args.get('username')
		if username is None:
			return jsonify({'success': 0, 'msg': 'invalid'})
		if User.query.filter_by(username = username).first() is not None:
			return jsonify({'success': 0, 'msg': 'invalid'})
	except:
		abort(500, "An unknown error occured whilst querying the database!")
	return jsonify({'success': 1, 'msg': 'valid'})

# Update User
#  You can update all the attributes of a user at once or you can just do it one by one
#
# POST /api/users/update
# Content-Type: application/json
#
# {"id": 1, "username": "jnunn", "name": "Jeremy N", "active": false}
#
###
@api.route('/users/update', methods=["POST"])
@auth.login_required
def users_update():
	try:
		id = request.json.get('id')
		username = request.json.get('username')
		name = request.json.get('name')
		active = request.json.get('active')
	except:
		abort(400, 'Missing Arguments')
	if id is None or (username is None and name is None and active is None):
		abort(400, 'Missing Arguments')
	try:
		u = User.query.filter_by(id = id).first()
		if u is None:
			abort(404, "No User Found!")
		if username:
			u.username = username
		if name:
			u.name = name
		if active in (True, False):
			u.active = active

		# Add to db
		db.session.commit()
	except Exception as e:
		print(e)
		abort(500, "An unknown error occured whilst trying to update a user!")
	return jsonify({'success': 1, 'msg': f"Successfully updated user {u.username}"})

# Delete a User
#
# POST /api/users/delete
# Content-Type: application/json
# 
# {"id": 1}
#
@api.route('/users/delete', methods=["POST"])
@auth.login_required
def delete_user():
	try:
		user_id = request.json.get('id')
	except:
		abort(400, 'Missing Arguments')
	if user_id is None:
		abort(400, 'Missing Arguments')
	try:
		User.query.filter_by(id = user_id).delete()
		db.session.commit()
	except:
		abort(500, 'An unknown error occured whilst trying to delte a User!')
	return jsonify({'success': 1, 'msg': f"Deleted user #{user_id} from the database!"})

# Create authentication token
#
# GET /api/token
# Authorization: Basic am51bm46cGFzc3dvcmQ=
#
##
@api.route('/token')
@auth.login_required
def create_auth_token():
	token = g.user.generate_auth_token()
	return jsonify({'success': 1, 'token': token.decode('ascii')})

# Test endpoint for testing authentication
# Token has to be base64 encoded and this authorization must be included for every api endpoint called
#
# GET /api/test
# Authorization: Basic <token>: 
#
#
@api.route('/test')
@auth.login_required
def protected():
	return jsonify({'success': 1, 'msg': f"Authenticated as: {entity_encode(g.user.name)}"})


## Asset 
#
# POST /api/assets/get
# Content-Type: application/json
# 
# {"tracking_code": "AA123"}
#
##
@api.route('/assets/get', methods=["POST"])
@auth.login_required
def get_asset():
	try:
		query = request.json.get('tracking_code')
	except:
		abort(400, "Missing Arguments")
	if query is None:
		abort(400, "Missing Arguments")
	query = query[1:] if query[0] == '#' else query
	results = {}
	try:
		asset = Assets.query.filter_by(tracking_code = query).first()
		if asset is None:
			abort(404, 'Asset not found!')
		results = {
			"tracking_code": entity_encode(asset.tracking_code),
			"type": entity_encode(asset.type),
			"time_created": asset.time_created,
			"status": entity_encode(asset.status[0].status),
			"def_location": entity_encode(asset.status[0].def_location),
			"location": entity_encode(asset.status[0].location),
			"note": entity_encode(asset.status[0].note),
			"last_updated": asset.status[0].last_updated
			}
	except Exception as e:
		print(e)
		abort(500, 'An unknown error occured whilst trying to get an asset!')
	return jsonify({'success': 1, 'results': results})

#
# Search the assets
#  This can be done through the asset tracking code or the type of asset currently
#
# POST /api/assets/search
# Content-Type: application/json
#
# {"query": "Compu"}
#
##
@api.route('/assets/search', methods=["POST", "GET"])
@auth.login_required
def search_assets():
	try:
		query = request.json.get('query')
	except:
		abort(400, "Missing Arguments")
	if query is None:
		abort(400, "Missing Arguments")
	query = query[1:] if query[0] == '#' else query
	query = f"{query}%"
	assets = Assets.query.filter(Assets.tracking_code.like(query)).all()
	if not assets:
		assets = Assets.query.filter(Assets.type.like(query)).all()
	if not assets:
		abort(404, "No Assets Found")
	results = []
	for a in assets:
		r = {
			"tracking_code": entity_encode(a.tracking_code),
			"type": entity_encode(a.type),
			"time_created": a.time_created,
			"status": entity_encode(a.status[0].status),
			"def_location": entity_encode(a.status[0].def_location),
			"location": entity_encode(a.status[0].location),
			"note": entity_encode(a.status[0].note),
			"last_updated": a.status[0].last_updated
			}
		results.append(r)
	return jsonify({"success": 1, "results": results})

# Add an Asset
#
# POST /api/assets/add
# Content-Type: application/json
# 
# {"type": "Computer", "tracking_code": "AB123", "note": "This computer is awesome, dont loose it!", "location": "VIC"}
#
##
@api.route('/assets/add', methods=["POST"])
@auth.login_required
def add_asset():
	try:
		asset_type = request.json.get('type')
		asset_code = request.json.get('tracking_code')
		asset_note = request.json.get('note')
		asset_status = request.json.get('status')
		asset_def_location = request.json.get('def_location')
		asset_location = request.json.get('location')
	except Exception as e:
		print(e)
		abort(400, "Missing Arguments")
	if asset_type is None or asset_code is None or asset_note is None or asset_status is None or asset_def_location is None or asset_location is None:
		abort(400, "Missing Arguments")
	if not (asset_status in ['faulty', 'available', 'moved', 'lost']):
		abort(400, "Missing Arguments")
	if Assets.query.filter_by(tracking_code = asset_code).first() is not None:
		abort(400, "Asset Tracking Code in USE!")
	asset_code = asset_code[1:] if asset_code[0] == '#' else asset_code
	try:
		# Create the asset
		asset = Assets(type = asset_type, tracking_code = asset_code)
		assetstatus = AssetStatus(ass_id = asset_code, status = asset_status, note = asset_note, def_location = asset_def_location, location = asset_location)
		# add to the db
		db.session.add(asset)
		db.session.add(assetstatus)
		db.session.commit()
	except:
		abort(500, "An unknown error occured whilst adding an asset to the database!")
	return jsonify({'success': 1, 'msg': 'Asset added to the database!'})

#
# Checks for valid asset IDs
#
@api.route('/assets/check', methods=['GET'])
@auth.login_required
def check_asset():
	try:
		code = request.args.get('id')
		if code is None:
			return jsonify({'success': 0, 'msg': 'invalid'})
		if Assets.query.filter_by(tracking_code = code).first() is not None:
			return jsonify({'success': 0, 'msg': 'invalid'})
	except:
		abort(500, "An unknown error occured whilst querying the database!")
	return jsonify({'success': 1, 'msg': 'valid'})

# Delete an asset
#
# POST /api/asset/delete
# Content-Type: application/json
# 
# {"tracking_code": "AB123"}
#
@api.route('/asset/delete', methods=["POST"])
@auth.login_required
def delete_asset():
	try:
		asset_code = request.json.get('tracking_code')
	except:
		abort(400, 'Missing Arguments')
	if asset_code is None:
		abort(400, 'Missing Arguments')
	asset_code = asset_code[1:] if asset_code[0] == '#' else asset_code
	try:
		assetstatus = AssetStatus.query.filter_by(ass_id = asset_code).first()
		# stores the retrieved assets state in AssetStatusLog table before deleting it
		save_deleted_asset(assetstatus.asset.type, assetstatus.ass_id, assetstatus.status, assetstatus.note, assetstatus.location, assetstatus.def_location)
		Assets.query.filter_by(tracking_code = asset_code).delete()
		AssetStatus.query.filter_by(ass_id = asset_code).delete()
		db.session.commit()
	except:
		abort(500, 'An unknown error occured whilst trying to delte an asset!')
	return jsonify({'success': 1, 'msg': f"Deleted Asset #{asset_code} from the database!"})

# Update Status
#  You can update all the attributes of a status at once or you can just do it one by one
#
# POST /api/assets/status/update
# Content-Type: application/json
#
# {"tracking_code": "AB123", "note": "I changed my mind, this computer sucks"}
#
###
@api.route('/asset/status/update', methods=["POST"])
@auth.login_required
def asset_status_update():
	try:
		asset_code = request.json.get('tracking_code')
		asset_type = request.json.get('type')
		status = request.json.get('status')
		note = request.json.get('note')
		def_location = request.json.get('def_location')
		location = request.json.get('location')
	except:
		abort(400, 'Missing Arguments')
	if asset_code is None or (asset_type is None and status is None and note is None and def_location is None and location is None):
		abort(400, 'Missing Arguments')
	asset_code = asset_code[1:] if asset_code[0] == '#' else asset_code
	try:
		assetstatus = AssetStatus.query.filter_by(ass_id = asset_code).first()
		# stores the retrieved assets state in AssetStatusLog table pre-modifying
		save_asset_history(assetstatus.asset.type, assetstatus.ass_id, assetstatus.status, assetstatus.note, assetstatus.location, assetstatus.def_location)
		if assetstatus is None:
			abort(404, "No Asset found!")
		if asset_type:
			assetstatus.asset.type = asset_type
		if status:
			assetstatus.status = status
		if note:
			assetstatus.note = note
		if def_location:
			assetstatus.def_location = def_location
		if location:
			assetstatus.location = location

		# Add to db
		#db.session.add(assetstatus)
		db.session.commit()
	except Exception as e:
		print(e)
		abort(500, "An unknown error occured whilst trying to update an asset!")
	return jsonify({'success': 1, 'msg': f"Successfully updated asset #{asset_code}"})

# used to enter the modified assets state pre-modification in the AssetStatusLog table
def save_asset_history(ass_type, ass_id, status, note, location, def_location):
	assetstatuslog = AssetStatusLog(type=ass_type, ass_id=ass_id, status=status, note=note, location=location, def_location=def_location) #version=0) #timestamp=currenttime)
	db.session.add(assetstatuslog)
	db.session.commit()
# used to enter the deleted assets state pre-deletion in the AssetStatusLog table
# appends a DELETED note
def save_deleted_asset(ass_type, ass_id, status, note, location, def_location):
	del_note = " DELETED"
	assetstatuslog = AssetStatusLog(type=ass_type + del_note, ass_id=ass_id, status=status, note=note + del_note, location=location, def_location=def_location) #version=0) #timestamp=currenttime)
	db.session.add(assetstatuslog)
	db.session.commit()
