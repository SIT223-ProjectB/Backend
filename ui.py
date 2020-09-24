#!/usr/bin/python3.7

from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, abort, request, g, session, render_template, redirect, url_for, send_file
import csv
from filter import entity_encode
from db import db, User, Assets, AssetStatus, AssetStatusLog

#
# User Verification for UI
#
def login_required(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		uid = session.get('user')
		if not uid:
			return redirect(url_for('ui.ui_login'))
		u = User.query.filter_by(id=int(uid), active=True).first()
		if not u:
			return redirect(url_for('ui.ui_login'))
		g.user = u
		return func(*args, **kwargs)
	return wrapper

#
# UI Blueprint
#
ui = Blueprint('ui', __name__)

#
# UI Context Processors
#
@ui.context_processor
def utility_processor():
	def escape(s):
		return entity_encode(s)

	def list_users_quick(limit=10):
		if limit<=0:
			limit = 1
		return [dict(username=u.username, name=u.name) for u in User.query.filter_by(active=True).all()][:limit]

	def list_users():
		return [dict(id=u.id, username=u.username, name=u.name, active=bool(u.active)) for u in User.query.all()]
	
	def get_all_assets():
		assets = []
		for a in AssetStatus.query.all():
			last_update = datetime.utcnow() - a.last_updated
			if last_update.days == 0:
				last_update = "Today"
			elif last_update.days == 1:
				last_update = "Yesterday"
			elif last_update < 7:
				last_update = f"{last_update.days} days ago"
			else:
				last_update = f"{last_update.weeks} weeks ago"
			assets.append(dict(id=a.ass_id, type=a.asset.type, last_update=last_update, status=a.status, def_location=a.def_location, location=a.location, note=a.note))
		return assets
	#gets all assets logs to display on logs.html
	def get_asset_log():
		log = []
		for a in AssetStatusLog.query.all():
			log.append(dict(id=a.ass_id, type=a.type, timestamp=a.timestamp, status=a.status, def_location=a.def_location, location=a.location, note=a.note))
		return log

	def latest_updated_assets(days=3, limit=10):
		date = datetime.utcnow() - timedelta(days=days)
		assets = []
		for a in AssetStatus.query.filter(AssetStatus.last_updated >= date).all():
			last_update = datetime.utcnow() - a.last_updated
			if last_update.days == 0:
				last_update = "Today"
			elif last_update.days == 1:
				last_update = "Yesterday"
			elif last_update < 7:
				last_update = f"{last_update.days} days ago"
			else:
				last_update = f"{last_update.weeks} weeks ago"
			assets.append(dict(id=a.ass_id, type=a.asset.type, last_update=last_update, status=a.status, def_location=a.def_location, location=a.location, note=a.note))
		return assets[:limit]

	return dict(list_users_quick=list_users_quick, list_users=list_users, get_all_assets=get_all_assets, latest_updated_assets=latest_updated_assets, escape=escape, get_asset_log=get_asset_log)

#
# UI Routes
# 
@ui.route('/login', methods=['GET'])
def ui_login():
	return render_template('login.html')

@ui.route('/register', methods=['GET'])
def ui_register():
	return render_template('register.html')

@ui.route('/', methods=['GET'])
@login_required
def ui_index():
	return render_template("index.html")

@ui.route('/assets', methods=['GET'])
@login_required
def ui_assets():
	return render_template('assets.html')

@ui.route('/logs', methods=['GET'])
@login_required
def ui_logs():
	return render_template('logs.html')

@ui.route('/users', methods=['GET'])
@login_required
def ui_users():
	return render_template('users.html')

@ui.route('/download', methods=['GET'])
@login_required
def download():
	def generate_logs():
		with open('downloads/logs.csv', 'w') as file:
			out = csv.writer(file)
			out.writerow(['Asset ID', 'Type', 'Status', 'Note','Location', 'Default Location', 'TimeStamp'])
			for a in db.session.query(AssetStatusLog).all():
				out.writerow([a.ass_id, a.type, a.status, a.note, a.location, a.def_location, a.timestamp])
		return True

	def generate_assets():
		with open('downloads/assets.csv', 'w') as file:
			out = csv.writer(file)
			out.writerow(['Asset ID', 'Type', 'Status', 'Note','Location', 'Default Location', 'Last_Updated'])
			for a in db.session.query(AssetStatus).all():
				out.writerow([a.ass_id, a.asset.type, a.status, a.note, a.location, a.def_location, a.last_updated])
		return True

	file = request.args.get('file')
	if not file:
		abort(404, 'Not found')

	try:
		file = str(file).lower()
		# Generate and send the logs file
		if file == "logs":
			generate_logs()
			return send_file('downloads/logs.csv', as_attachment=True, attachment_filename='All_Logs.csv')
		# Generate and send the assets file
		if file == "assets":
			generate_assets()
			return send_file('downloads/assets.csv', as_attachment=True, attachment_filename='All_Assets.csv')
	except:
		pass
	# No file found
	abort(404, "Not Found")


