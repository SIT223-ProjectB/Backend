#!/usr/bin/python3.7

from flask import Blueprint, jsonify, abort, request, g, redirect, session, url_for
from flask_httpauth import HTTPBasicAuth

from db import db, User, Assets, AssetStatus

api = Blueprint('api', __name__)
auth = HTTPBasicAuth()

#
# Password Verification
# 
@auth.verify_password
def _verify_password(username_or_tok, password):
	# Try to verify based on session
	uid = session.get('user')
	if not uid:
		return redirect(url_for('ui.ui_login'))
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
	return jsonify({'success': 1, 'msg': f"Authenticated as: {g.user.name}"})


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
			"tracking_code": asset.tracking_code,
			"type": asset.type,
			"time_created": asset.time_created,
			"status": asset.status[0].status,
			"location": asset.status[0].location,
			"note": asset.status[0].note,
			"last_updated": asset.status[0].last_updated
			}
	except:
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
			"tracking_code": a.tracking_code,
			"type": a.type,
			"time_created": a.time_created,
			"status": a.status[0].status,
			"location": a.status[0].location,
			"note": a.status[0].note,
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
		asset_location = request.get('location')
	except:
		abort(400, "Missing Arguments")
	if asset_type is None or asset_code is None or asset_note is None or asset_location is None:
		abort(400, "Missing Arguments")
	if Assets.query.filter_by(tracking_code = asset_code).first() is not None:
		abort(400, "Asset Tracking Code in USE!")
	asset_code = asset_code[1:] if asset_code[0] == '#' else asset_code
	try:
		# Create the asset
		asset = Assets(type = asset_type, tracking_code = asset_code)
		assetstatus = AssetStatus(ass_id = asset_code, note = asset_note, location = asset_location)
		# add to the db
		db.session.add(asset)
		db.session.add(assetstatus)
		db.session.commit()
	except:
		abort(500, "An unknown error occured whilst adding an asset to the database!")
	return jsonify({'success': 1, 'msg': 'Asset added to the database!'})

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
		Assets.query.filter_by(tracking_code = asset_code).delete()
		AssetStatus.query.filter_by(ass_id = asset_code).delete()
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
		status = request.json.get('status')
		note = request.json.get('note')
		location = request.json.get('location')
	except:
		abort(400, 'Missing Arguments')
	if asset_code is None or (status is None and note is None and location is None):
		abort(400, 'Missing Arguments')
	asset_code = asset_code[1:] if asset_code[0] == '#' else asset_code
	try:
		assetstatus = AssetStatus.query.filter_by(ass_id = asset_code).first()
		if assetstatus is None:
			abort(404, "No Asset found!")
		if status:
			assetstatus.status = status
		if note:
			assetstatus.note = note
		if location:
			assetstatus.location = location
		# Add to db
		db.session.add(assetstatus)
		db.session.commit()
	except:
		abort(500, "An unknown error occured whilst trying to update the status of an asset!")
	return jsonify({'success': 1, 'msg': f"Successfully updated the status of asset #{asset_code}"})
