#!/usr/bin/python3.7


from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from config import current_config

##
# app Setup
##

app = Flask(__name__)
app.config.from_object(current_config)

##
# Authorization Required &
# Wrong HTTP Method / Resource not found
##
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(405)
@app.errorhandler(404)
def _app_errors(e):
	return jsonify({'success': 0, 'error': str(e)}), 404

##
# Database Connection
##
db = SQLAlchemy(app)

##
# Blueprint Registering
##
from api import api as api_routes

app.register_blueprint(api_routes, url_prefix='/api')
