#!/usr/bin/python3.7

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import current_config

app = Flask(__name__)
app.config.from_object(current_config)


db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(120), nullable=False)
	name = db.Column(db.String(120), nullable=False)
	active = db.Column(db.Boolean, default=False)

db.create_all()