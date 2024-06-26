import os

class ProductionConfig:
    
    # Get the base directory of your app--
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Development-specific configurations--
    #FLASK_DEBUG=0

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'finance.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # External folder config to the filters and validators    
    CUSTOM_FLASKWTF_PATH = os.environ.get('CUSTOM_FLASKWTF_PATH')

    # Session configuration
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'

    # Get the port number from the PORT environment variable (default is 10000)
    PORT = int(os.getenv('PORT', 5000))
    print(f'running config_prod ... PORT is: { PORT }')

    # Pull in secret key from .env
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

    # Content Security Policy for Talisman
    CONTENT_SECURITY_POLICY = {
    'default-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
        'https://cdnjs.cloudflare.com',
    ],
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
        'https://code.jquery.com/',
    ],
    'style-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',  # Allow styles from cdn.jsdelivr.net
        'https://cdnjs.cloudflare.com',  # Allow styles from cloudflare CDN (for Font Awesome)
        '\'unsafe-inline\'',
    ],
    'img-src': [
        "'self'",
        "data:",  # Allows data URIs for images
        "https://financialmodelingprep.com/", # Allowed bc image used for /quoted
    ],
    'report-uri': '/csp-violation-report'
    }

    # Logging configurations
    LOG_TO_CONSOLE = False
    LOG_TO_FILE = True
    LOG_FILE_PATH = os.path.join(BASEDIR, 'logs', 'app.log')

    # Email server configuration for development
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
