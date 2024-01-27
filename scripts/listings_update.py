import os
import sys
# Add the project root directory to the Python path to allow for correct module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from myFinance50_helpers import update_listings, fmp_key


# Can pass an argument to create_app (testing, development, etc.) if desired.
app = create_app()


def run_scheduled_task():
    with app.app_context():
        update_listings(fmp_key)

if __name__ == '__main__':
    run_scheduled_task()