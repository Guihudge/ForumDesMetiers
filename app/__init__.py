from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import sqlalchemy as sa
import secrets


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


from app import routes, models

with app.app_context():
    # Init db if empty
    try:
        users = db.session.scalars(sa.select(models.User)).all()
        if len(users) == 0:
            print("New db, initialize...")
            password_length = 13
            password = secrets.token_urlsafe(password_length)
            u = models.User(username="admin", displayName="Administrator", classe="")
            u.set_password(password)
            u.set_access(100)
            print(f"Username: admin\tpassword: {password}")
            db.session.add(u)
            db.session.commit()
    except:
        print("Whoa, first database query failed...")
        print("Try reinit db")
        db.create_all()
