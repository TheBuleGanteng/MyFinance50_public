#!/usr/bin/env python3

import os
import sys
# Add the project root directory to the Python path to allow for correct module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from myFinance50_helpers import purge_unconfirmed_accounts


# Can pass an argument to create_app (testing, development, etc.) if desired.
app = create_app()


def run_scheduled_task():
    with app.app_context():
        purge_unconfirmed_accounts()

if __name__ == '__main__':
    run_scheduled_task()