#!/usr/bin/python3.7

from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, abort, request, g, session, render_template, redirect, url_for

from db import db, User, Assets, AssetStatus

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
	def list_users_quick(limit=10):
		if limit<=0:
			limit = 1
		return [dict(username=u.username, name=u.name) for u in User.query.filter_by(active=True).all()][:limit]
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
			assets.append(dict(id=a.ass_id, type=a.asset.type, last_update=last_update))
		return assets[:limit]

	return dict(list_users_quick=list_users_quick, latest_updated_assets=latest_updated_assets)

#
# UI Routes
# 
@ui.route('/', methods=['GET'])
@login_required
def ui_index():
	return render_template("index.html")

@ui.route('/login', methods=['GET'])
def ui_login():
	return render_template('login.html')