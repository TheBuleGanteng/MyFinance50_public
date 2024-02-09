import os
from .helpers import receive_email_address, send_email

def aggregate_logs(log_file_path):
    """Reads the log file and returns its contents."""
    with open(log_file_path, 'r') as file:
        return file.read()

def main():
    # Get the base directory of your app--
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Update with the path to your log file
    log_file_path = os.path.join(BASEDIR, 'logs', 'app.log')
    logs = aggregate_logs(log_file_path)
    send_email(body=logs, recipient=receive_email_address)

if __name__ == "__main__":
    main()