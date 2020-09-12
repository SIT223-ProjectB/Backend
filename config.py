#!/usr/bin/python3.7

##
# Current Configuration class
##
current_config = "config.DevelopmentConfig"
#current_config = "config.ProductionConfig"

##
# Configurations
##

class DefaultConfig():
	# Flask
	DEBUG=False
	TESTING=False
	SECRET_KEY=None
	JSON_SORT_KEYS=False
	# Flask - Sessions
	SESSION_COOKIE_SAMESITE='Strict'
	SESSION_COOKIE_HTTPONLY=False
	SESSION_COOKIE_SECURE=False
	SESSION_TYPE = "filesystem"
	PERMANENT_SESSION_LIFETIME = 1800
	# Flask-SQLAlchemy
	SQLALCHEMY_TRACK_MODIFICATIONS=False

class DevelopmentConfig(DefaultConfig):
	DEBUG=True
	TESTING=True
	SECRET_KEY='this_is_a_secret_key'
	# Flask-SQLAlchemy
	SQLALCHEMY_DATABASE_URI='sqlite:///test.db'

class ProductionConfig(DefaultConfig):
	DEBUG=False
	TESTING=False
	SECRET_KEY='Randomized_Secret_Everytime_Here'
	# Flask-SQLAlchemy
	SQLALCHEMY_DATABASE_URI='mysql://user:pw@localhost/db_name'
