from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Initialize Flask and SQLAlchemy.
app = Flask(__name__)
app.config.from_object('webConfig')
db = SQLAlchemy(app)

SERVER_PORT = 3000

# Circular dependency, but this is okay. See
# http://flask.pocoo.org/docs/0.10/patterns/packages/ for more info.
from webFiles import views, models
