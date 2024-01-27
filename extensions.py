from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman


db = SQLAlchemy()
csrf = CSRFProtect()
#mail = Mail()
#oauth = OAuth()
talisman = Talisman()
load_dotenv()
