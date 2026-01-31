# It's okay man
import datetime
import os
from flask import Flask
from flask_session import Session
from dotenv import load_dotenv

from sitezinho.models.database import db
from sitezinho.services.config_service import initialize_default_configs

from sitezinho.routes.views import views
from sitezinho.routes.api import api

FILENAME = "artes.zip"
f = open("logs.txt", "a")
load_dotenv()


mysql_url = os.getenv("mysql_url")
if not mysql_url:
    raise RuntimeError("mysql_url environment variable not set. Check .env")


app = Flask(__name__)

mysql_url = os.getenv("mysql_url")
f.write(f"{mysql_url} \n")
print(mysql_url)
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SERIALIZATION_FORMAT"] = 'json'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 280}
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
app.config["SESSION_REFRESH_EACH_REQUEST"] = False
app.secret_key = os.getenv("secret_key")
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
)

# Initialize db with app
db.init_app(app)
app.config["SESSION_SQLALCHEMY"] = db
Session(app)

with app.app_context():
    db.create_all()
    # Initialize default configurations
    initialize_default_configs()


app.register_blueprint(views)
app.register_blueprint(api)
