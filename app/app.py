from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from app import config



app = Flask(__name__)
app.config.from_object(config)

Bootstrap(app)	
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# Registro de los Blueprints
from .usuarios import usuarios_bp
app.register_blueprint(usuarios_bp)


from .contactos import contactos_bp
app.register_blueprint(contactos_bp)

from .etiquetas import etiquetas_bp
app.register_blueprint(etiquetas_bp)
