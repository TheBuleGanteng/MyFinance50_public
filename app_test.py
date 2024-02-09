from app import create_app, db as test_db
from configs.config_testing import TestingConfig
from datetime import date, datetime
from flask import url_for
from helpers import generate_unique_token, verify_unique_token
from models import User, Transaction
import pytest
import re
from unittest.mock import patch, MagicMock
from urllib.parse import unquote
import uuid
from werkzeug.security import generate_password_hash



# Setup steps summary: 
# Setup step 1: Creates instance of app and test DB, awaits tests, and then tears down
# Setup step 2: Creates virtual CLI used to execute tests
# Setup step 3: Creates a timestamp that can be added to print statements to aid debugging
# Setup step 4: Declare global variable for test number
# Setup step 5: Create an instance of app.py for testing.
# Setup step 6: Defines function to clear the users table
# Setup step 7: Defines function to create a token for password reset
# Setup step 8: Define global variable for unhashed password
# Setup step 9: Defines function to CREATE an UNCONFIRMED test user
# Setup step 10: Defines function to CREATE a CONFIRMED test user
# Setup step 11: Defines function to DELETE an UNCONFIRMED test user
# Setup step 12: Defines function to DELETE a CONFIRMED test user


# Setup step 1: Create instance of app w/ testing config, create test DB, wait for tests 
# to complete, and then delete test DB from memory.
@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        test_db.create_all()
        yield app  # This is where the testing happens
        test_db.drop_all()


# Setup step 2: Create runner representing virtual CLI into which programs 
# will enter commands for testing.
@pytest.fixture(scope='module')
def runner(app):
    return app.test_cli_runner()


# Setup step 3: Creates a timestamp that can be added to print statements to aid debugging
execution_order_counter = 0
def get_execution_order():
    global execution_order_counter
    execution_order_counter += 1
    return execution_order_counter


# Setup step 4: Declare global variable for test number
test_number = 0


# Setup step 5: Create an instance of app.py for testing.
@pytest.fixture(scope='function')
def client():
    app = create_app('testing')  # Create the test app
    with app.test_client() as test_client:
        yield test_client


# Setup step 6: Define function to clear the users and transactions tables
def clear_tables(test_app):
    with test_app.app_context():
        User.query.delete()
        Transaction.query.delete()
        test_db.session.commit()


# Setup step 7: Define global variable for unhashed password
test_password_unhashed = 'GLBMjKJ3qphUodwvqyF!+-=' 


# Setup step 8: Defines function to create a token for password reset
def generate_real_token_for_test_user(test_user, app):
    # Directly use the SECRET_KEY from the app's config
    secret_key = app.config['SECRET_KEY']
    real_token = generate_unique_token(test_user.id, secret_key)
    return real_token


# Setup step 9: Defines function to CREATE an UNCONFIRMED test user in the DB where confirmed = 0
def insert_test_user_unconfirmed(test_app):
    with test_app.app_context():
        test_user_email = f'{uuid.uuid4()}@mattmcdonnell.net'
        test_password_hashed = generate_password_hash(test_password_unhashed)
        test_user = User(
            name_first='Pytest_Name_First',
            name_last='Pytest_Name_Last',
            username='PytestUser',
            email=test_user_email,
            confirmed='No',
            created=datetime.now(),
            hash=test_password_hashed,
            cash=10000,
            accounting_method='FIFO',
            tax_loss_offsets='On',
            tax_rate_STCG=30,
            tax_rate_LTCG=15,
            cash_initial=10000,            
        )
        test_db.session.add(test_user)
        try:
            test_db.session.commit()
        except Exception as e:
            print(f'{get_execution_order()} -- running insert_test_user_unconfirmed(app)... error during commit is: { e }')
            return None
        user_data_unconfirmed_user = User.query.filter_by(email=test_user_email).first()
        if user_data_unconfirmed_user:
            print(f'{get_execution_order()} -- running insert_test_user_unconfirmed(app)... user_data_unconfirmed_user is: { user_data_unconfirmed_user }')
            return user_data_unconfirmed_user
        else:
            print(f'{get_execution_order()} -- running insert_test_user_unconfirmed(app)... no user_data_unconfirmed_user created')
            return None


# Setup step 10: Defines function to CREATE a CONFIRMED test user in the DB
def insert_test_user_confirmed(test_app):
    with test_app.app_context():
        test_user_email = f'{uuid.uuid4()}@mattmcdonnell.net'
        test_password_hashed = generate_password_hash(test_password_unhashed)
        test_user = User(
            name_first='Pytest_Name_First',
            name_last='Pytest_Name_Last',
            username='PytestUser',
            email=test_user_email,
            confirmed='Yes',
            created=datetime.now(),
            hash=test_password_hashed,
            cash=10000,
            accounting_method='FIFO',
            tax_loss_offsets='On',
            tax_rate_STCG=30,
            tax_rate_LTCG=15,
            cash_initial=10000,
        )
        test_db.session.add(test_user)
        try:
            test_db.session.commit()
        except Exception as e:
            print(f'{get_execution_order()} -- running insert_test_user_confirmed(app)... error during commit is: { e }')
            return None
        user_data_test_user = User.query.filter_by(email=test_user_email).first()
        if user_data_test_user:
            print(f'{get_execution_order()} -- running insert_test_user_confirmed(app)... user_data_test_user is: { user_data_test_user }')
            return user_data_test_user
        else:
            print(f'{get_execution_order()} -- running insert_test_user_confirmed(app)... no user_data_test_user created')
            return None


# Setup step 11: Defines function to DELETE the UNCONFIRMED test user
def delete_test_user_unconfirmed(email, test_app):
    with test_app.app_context():
        user_data_unconfirmed_user = User.query.filter_by(email=email).first()
        if user_data_unconfirmed_user:
            print(f'{get_execution_order()} -- running delete_test_user_unconfirmed(email, app)... user_data_unconfirmed_user is: { user_data_unconfirmed_user }')
            test_db.session.delete(user_data_unconfirmed_user)
            test_db.session.commit()
            print(f'{get_execution_order()} -- running delete_test_user_unconfirmed(email, app)... user_data_unconfirmed_user deleted from session')
        else:
            print(f'{get_execution_order()} -- running delete_test_user_unconfirmed(email)... no user_data_unconfirmed_user found in DB.')


# Setup step 12: Defines function to DELETE the CONFIRMED test test user
def delete_test_user_confirmed(email,test_app):
    with test_app.app_context():
        user_data_test_user = User.query.filter_by(email=email).first()
        if user_data_test_user:
            print(f'{get_execution_order()} -- running delete_test_user_confirmed(email, app)... user_data_test_user is: { user_data_test_user }')
            test_db.session.delete(user_data_test_user)
            test_db.session.commit()
            print(f'{get_execution_order()} -- running delete_test_user_confirmed(email, app)... user_data_test_user deleted from session')
        else:
            print(f'{get_execution_order()} -- running delete_test_user_confirmed(email)... no user_data_test_user found in DB.')
     


# ---------------------------------------------------------------------------------------------------------------
# Testing route: /login
# Summary: 
# Test 1: login.html returns code 200
# Test 2: Happy path (valid email+valid pw)
# Test 3: User attempts to log in w/o valid CSRF token.
# Test 4: No CSP headers in page
# Test 5: No email entered
# Test 6: No PW entered
# Test 7: No email + no PW entered
# Test 8: Undeliverable email entered
# Test 9: Unregistered email
# Test 10: Registered email + wrong pw
# Test 11: Unregistered email + wrong pw
# Test 12: User tries to log in w/ unconfirmed account


# /login Test 1: login.html returns code 200
def test_code_200_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 2: Happy Path: user logs in w/ valid  email address + valid password --> user redirected to / w/ success message.
def test_happy_path_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)

    assert response.request.path == '/'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 3: User attempts to log in w/o valid CSRF token.
def test_missing_CSRF_login(client):
    #db = setup_test_database()
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... returned status code 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': 'invalid_token',
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)

    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 4: Tests for presence of CSP headers in page.
def test_csp_headers_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 5: User does not submit email address
def test_missing_email_address_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': '',
        'password': test_password_unhashed
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 6: User does not submit PW
def test_missing_pw_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': '',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 7: User does not submit username or password  --> is redirected 
# to /login and flashed message.
def test_missing_email_missing_pw_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': '',
        'password': '',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 8: User enters undeliverable email address.
def test_undeliverable_email_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return
    
    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': 'matt',
        'password': test_password_unhashed,
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 9: User tries to log in w/ unregistered email address + correct PW
def test_with_unregistered_email_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': 'unregistered@mattmcdonnell.net',
        'password': test_password_unhashed,
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 10: User tries to log in w/ registered email address + invalid PW
def test_with_invalid_pw_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': 'InvalidPassword',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 11: User tries to log in w/ unregistered email address + invalid PW
def test_with_invalid_username_invalid_pw_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': 'unregistered@mattmcdonnell.net',
        'password': 'InvalidPassword',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 12: User tries to log in w/ unconfirmed account
def test_for_unconfirmed_user_login(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create test user
    test_user = insert_test_user_unconfirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode()
    print("HTML:", html)
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    print("CSRF Token:", csrf_token)

    # Simulate a POST request to /login
    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed,
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')




# ---------------------------------------------------------------------------------------------------------------
# Testing route: /register
# Summary: 
# Test 13: login.html returns code 200
# Test 14: Happy path, scenario a --> sends email & user redirected to /index
# Test 15: User attempts to log in w/o valid CSRF token.
# Test 16: No CSP headers in page
# Test 17: Missing req. field: email address
# Test 18: Missing req. field: username
# Test 19: Missing req. field: password
# Test 20: Missing req. field: password confirmation
# Test 21: Password fails strength test (uses pw = 'a' for test) 
# Test 22: PW =! PW confirmation 
# Test 23: User enters illegitimate email address.
# Test 24: User enters prohibited char in any user inputs (using '>' as test)
# Test 25: User enters an already-registered username.
# Test 26: User enters an already-registered email address.
   

# /register Test 13: register.html returns code 200
def test_code_200_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/register')
    assert response.status_code == 200
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 14: Happy path, all req. info --> sends email & user redirected to /index
def test_happy_path_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        print(f'{get_execution_order()} -- running test number: { test_number }... url_map is: { client.application.url_map }')
        print(f'{get_execution_order()} -- running test number: { test_number }... app config is: { client.application.config }')
        
        response = client.get('/register')
        if response.status_code != 200:
            print(f'{get_execution_order()} -- running test number: { test_number }... response.status_code is: { response.status_code }')
            print(f'{get_execution_order()} -- running test number: { test_number }... response body is: { response.data.decode() }')    
        assert response.status_code == 200, f'{get_execution_order()} -- running test number: { test_number }... Failed to load /register. Check route availability in test setup.'
        print(f'{get_execution_order()} -- running test number: { test_number }... response code for register.html was 200')

        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        print(f'{get_execution_order()} -- running test number: { test_number }... csrf_token is: { csrf_token }')

        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)
        print(f'{get_execution_order()} -- running test number: { test_number }... response is: { response }')

        mock_send.assert_called_once()
        print(f'{get_execution_order()} -- running test number: { test_number }... email mock sent to user')
        assert response.request.path == '/login'
        print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to login')
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 15: User attempts to log in w/o valid CSRF token.
def test_missing_CSRF_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None
    
        # Create test user in test DB.
        test_user = insert_test_user_confirmed(client.application)

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Simulate a POST request to /register
        response = client.post('/register', data={
            'csrf_token': 'csrf_token',
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 16: Tests for presence of CSP headers in page.
def test_csp_headers_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to a page and check for status 200
        response = client.get('/register')
        assert response.status_code == 200

        # Check if CSP headers are set correctly in the response
        csp_header = response.headers.get('Content-Security-Policy')
        assert csp_header is not None
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 17: Missing user email address.
def test_missing_email_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': ' ',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 18: Missing username.
def test_missing_username_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': ' ',
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 19: Missing PW.
def test_missing_pw_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': ' ',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 20: Missing PW confirmation.
def test_missing_pw_confirm_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None
    
        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': ' ',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)
    
        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 21: Fails pw strength.
def test_pw_strength_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': 'a',
            'password_confirmation': 'a',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 22: PW != PW confirmation.
def test_pw_mismatch_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw1234',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 23: User enters illegitimate email address.
def test_bad_email_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'testmattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 24: User enters prohibited chars.
def test_prohibited_chars_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest>NameFirst',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 25: User enters an already-registered username.
def test_duplicate_username_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        test_user = insert_test_user_confirmed(client.application)

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': test_user.username,
            'email': 'test@mattmcdonnell.net',
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /register Test 26: User enters an already-registered email address.
def test_duplicate_email_register(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        # Configure the mock to do nothing
        mock_send.return_value = None

        test_user = insert_test_user_confirmed(client.application)

        # Make a GET request to the register page to get the CSRF token
        response = client.get('/register')
        assert response.status_code == 200
        html = response.data.decode()
        csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
        
        response = client.post('/register', data={
            'csrf_token': csrf_token,
            'name_first': 'Pytest_Name_First',
            'name_last': 'Pytest_Name_Last',
            'username': 'PytestUser',
            'email': test_user.email,
            'password': 'tGLBMjKJ3qphUodw123',
            'password_confirmation': 'tGLBMjKJ3qphUodw123',
            'cash_initial': '10000',
            'accounting_method': 'FIFO',
            'tax_loss_offsets': 'On',
            'tax_rate_STCG': '30',
            'tax_rate_LTCG': '15',
        }, follow_redirects=True)

        mock_send.assert_not_called()
        assert response.request.path == '/register'
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /profile
# Summary: 
# Test 27: profile.html returns code 200
# Test 28: Happy path (all req. fields, valid email, username, pw)
# Test 29: User attempts to log in w/o valid CSRF token.
# Test 30: Tests for presence of CSP headers in page.
# Test 31: Failed allowed chars check on user input (using > in first name)

# /profile Test 27: register.html returns code 200
def test_login_code_200_profile(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/profile')
    assert response.status_code == 200
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /profile Test 28: Happy path to updating profile (note: not all fields need be filled)
def test_happy_path_profile(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/profile')
    assert response.status_code == 200

    profile_response = client.post('/profile', data={
        'csrf_token': csrf_token,
        'name_first': 'John',
        'name_last': 'Doe',
        'username' : 'UnusedUsername',
        'accounting_method': 'LIFO',
        'tax_loss_offsets': 'Off',
        'tax_rate_STCG': '10',
        'tax_rate_LTCG': '35',
    }, follow_redirects=True)

    assert profile_response.request.path == '/profile'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /profile after submission of updated data')
    
    # Fetch the updated user data from the database
    updated_user = User.query.filter_by(email=test_user.email).first()
    print(f'{get_execution_order()} -- running test number: { test_number }... pulled updated_user from DB: { updated_user }')

    # Verify the updated fields
    assert updated_user.name_first == 'John'
    assert updated_user.name_last == 'Doe'
    assert updated_user.username == 'UnusedUsername'
    assert updated_user.accounting_method == 'LIFO'
    assert updated_user.tax_loss_offsets == 'Off'
    assert updated_user.tax_rate_STCG == 10
    assert updated_user.tax_rate_LTCG == 35
    print(f'{get_execution_order()} -- running test number: { test_number }... all updated data is now reflected in DB')

    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /profile Test 29: User attempts to log in w/o valid CSRF token.
def test_missing_CSRF_profile(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/profile')
    assert response.status_code == 200

    profile_response = client.post('/profile', data={
        'csrf_token': 'invalid_token',
        'name_first': 'John',
        'name_last': 'Doe',
        'username' : 'UnusedUsername',
        'accounting_method': 'LIFO',
        'tax_loss_offsets': 'Off',
        'tax_rate_STCG': '10',
        'tax_rate_LTCG': '35',
    }, follow_redirects=True)

    # Check for a 400 Bad Request response
    assert profile_response.status_code == 400, f"Expected 400 Bad Request, got {profile_response.status_code}"

    assert profile_response.request.path == '/profile'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /profile after submission of updated data')

    # Fetch the updated user data from the database
    updated_user = User.query.filter_by(email=test_user.email).first()
    print(f'{get_execution_order()} -- running test number: { test_number }... pulled updated_user from DB: { updated_user }')

    # Verify that the originally pulled data remains in the DB
    assert updated_user.name_first == test_user.name_first
    assert updated_user.name_last == test_user.name_last
    assert updated_user.username == test_user.username
    assert updated_user.accounting_method == test_user.accounting_method
    assert updated_user.tax_loss_offsets == test_user.tax_loss_offsets
    assert updated_user.tax_rate_STCG == test_user.tax_rate_STCG
    assert updated_user.tax_rate_LTCG == test_user.tax_rate_LTCG
    print(f'{get_execution_order()} -- running test number: { test_number }... orig. data remains in DB')

    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /profile Test 30: Tests for presence of CSP headers in page.
def test_csp_headers_profile(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/profile')
    assert response.status_code == 200

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /profile Test 31: Failed allowed chars check on user input (using > in first name)
def test_prohibited_chars_profile(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/profile')
    assert response.status_code == 200

    profile_response = client.post('/profile', data={
        'csrf_token': csrf_token,
        'name_first': 'Joh>n',
        'name_last': 'Doe',
        'username' : 'UnusedUsername',
        'accounting_method': 'LIFO',
        'tax_loss_offsets': 'Off',
        'tax_rate_STCG': '10',
        'tax_rate_LTCG': '35',
    }, follow_redirects=True)

    # Check for a 200 Bad Request response
    assert profile_response.status_code == 200, f"Expected 200, got {profile_response.status_code}"
    assert "Invalid input" in profile_response.data.decode()

    assert profile_response.request.path == '/profile'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /profile after submission of updated data')

    # Fetch the updated user data from the database
    updated_user = User.query.filter_by(email=test_user.email).first()
    print(f'{get_execution_order()} -- running test number: { test_number }... pulled updated_user from DB: { updated_user }')

    # Verify that the originally pulled data remains in the DB
    assert updated_user.name_first == test_user.name_first
    assert updated_user.name_last == test_user.name_last
    assert updated_user.username == test_user.username
    assert updated_user.accounting_method == test_user.accounting_method
    assert updated_user.tax_loss_offsets == test_user.tax_loss_offsets
    assert updated_user.tax_rate_STCG == test_user.tax_rate_STCG
    assert updated_user.tax_rate_LTCG == test_user.tax_rate_LTCG
    print(f'{get_execution_order()} -- running test number: { test_number }... orig. data remains in DB')

    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /password_change
# Summary: 
# Test 32: password_change.html returns code 200
# Test 33: Happy path (all req. fields, valid email, username, pw)
# Test 34: User attempts to log in w/o valid CSRF token.    
# Test 35: Tests for presence of CSP headers in page.
# Test 36: No user email submitted
# Test 37: No current password submitted
# Test 38: No new password submitted
# Test 39: No new password confirmation submitted
# Test 40: New password does not meet strength requirements
# Test 41: New password and new password confirmation don't match
# Test 42: User-entered email is not registered in DB
# Test 43: User entered incorrect value for current PW


# /pw_change Test 32: pw_change.html returns code 200
def test_login_code_200_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /pw_change Test 33: Happy path
def test_happy_path_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': test_password_unhashed,
        'password': 'test1234',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
    
    assert response.request.path == '/'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 34: /pw_change User attempts to log in w/o valid CSRF token.
def test_missing_csrf_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': 'invalid_token',
        'email': test_user.email,
        'password_old': test_password_unhashed,
        'password': 'test1234',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
    
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 35: Tests for presence of CSP headers in page.
def test_csp_headers_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None


# Test 36: /pw_change No user email submitted
def test_missing_user_email_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': ' ',
        'password_old': test_password_unhashed,
        'password': 'test1234',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 37: /pw_change No current pw submitted
def test_missing_pw_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': ' ',
        'password': 'test1234',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 38: /pw_change No new pw submitted
def test_missing_new_pw_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': test_password_unhashed,
        'password': ' ',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 39: /pw_change No new pw confirmation submitted
def test_missing_new_pw_confirm_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': test_password_unhashed,
        'password': 'test1234',
        'password_confirmation': ' '
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 40: /pw_change New password does not meet strength requirements
def test_insufficient_pw_strength_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': test_password_unhashed,
        'password': 'a',
        'password_confirmation': 'a'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 41: /pw_change New password and new password confirmation don't match
def test_mismatching_pws_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': test_password_unhashed,
        'password': 'test1234',
        'password_confirmation': 'test12345'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 42: /pw_change User-entered email is not registered in DB
def test_unregistered_email_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': 'unregistered@mattmcdonnell.net',
        'password_old': test_password_unhashed,
        'password': 'test1234',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 43: /pw_change User entered incorrect value for current PW
def test_incorrect_current_pw_pw_change(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_change')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... password_change returned code 200')

    response = client.post('/password_change', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password_old': 'incorrect_password',
        'password': 'test1234',
        'password_confirmation': 'test1234'
    }, follow_redirects=True) 
 
    assert response.request.path == '/password_change'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /pw_reset_req
# Summary: 
# Test 44: password_reset_request.html returns code 200
# Test 45: Happy path (all req. fields, valid email, username, pw)
# Test 46: User attempts to log in w/o valid CSRF token.    
# Test 47: Tests for presence of CSP headers in page.
# Test 48: No user email submitted
# Test 49: Prohibited chars in user-submitted email address
# Test 50: User submits an invalid email address format.
# Test 51: User submits unregistered email address


# /password_reset_request Test 44: password_reset_request.html returns code 200
def test_login_code_200_password_reset_request(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /password_reset_request Test 45: Happy path
def test_happy_path_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Mock the mail.send function
    with patch('app.send_email') as mock_send_mail:
        # Configure the mock to do nothing
        mock_send_mail.return_value = None

        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token,
            'email': test_user.email
        }, follow_redirects=True)

        # Assert that the mock was called
        mock_send_mail.assert_called_once()
        print(f'{get_execution_order()} -- running test number: { test_number }... email sent to user')

    assert response.request.path == '/login'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /pw_reset_req Test 46: User attempts to log in w/o valid CSRF token.
def test_missing_csrf_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)

    # Make a GET request to the login page to get the CSRF token
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... returned 200 code')

    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /pw_reset_req Test 47: Tests for presence of CSP headers in page.
def test_missing_csp_headers_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None
    print(f'{get_execution_order()} -- running test number: { test_number }... csp_header found')

    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /pw_reset_req Test 48: User submitted no value for email
def test_missing_email_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Mock the mail.send function
    with patch('app.send_email') as mock_send_mail:
        # Configure the mock to do nothing
        mock_send_mail.return_value = None

        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token,
            'email': ' '
        }, follow_redirects=True)

    assert response.request.path == '/password_reset_request'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 49: /pw_reset_req User submitted prohibited chars
def test_invalid_chars_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Mock the mail.send function
    with patch('app.send_email') as mock_send_mail:
        # Configure the mock to do nothing
        mock_send_mail.return_value = None

        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token,
            'email': '>'+test_user.email
        }, follow_redirects=True)

    assert response.request.path == '/password_reset_request'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 50: /pw_reset_req User submits an invalid email address format.
def test_invalid_email_format_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Mock the mail.send function
    with patch('app.send_email') as mock_send_mail:
        # Configure the mock to do nothing
        mock_send_mail.return_value = None

        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token,
            'email': 'unregisteredatmattmcdonnell.net'
        }, follow_redirects=True)

    assert response.request.path == '/password_reset_request'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# Test 51: /pw_reset_req User-entered email not in database
def test_unregistered_email_pw_reset_req(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/password_reset_request')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Mock the mail.send function
    with patch('app.send_email') as mock_send_mail:
        # Configure the mock to do nothing
        mock_send_mail.return_value = None

        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token,
            'email': 'unregistered@mattmcdonnell.net'
        }, follow_redirects=True)

    assert response.request.path == '/login'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /pw_reset_new
# Summary:
# Test 52: password_reset_request_new.html returns code 200
# Test 53: Happy path (all req. fields, valid email, username, pw)
# Test 54: User attempts to log in w/o valid CSRF token.    
# Test 55: Tests for presence of CSP headers in page.
# Test 56: User submits invalid token via GET
# Test 57: Missing value for pw_reset_new
# Test 58: Missing value for pw_reset_new_confirm
# Test 59: Missing value for pw_reset_new and pw_reset_new_confirm    
# Test 60: User enters prohibited chars
# Test 61: User enters insufficiently strong PW
# Test 62: Mismatching pw_reset_new and pw_reset_new_confirm
# Test 63: New password matches old password


# /pw_reset_new Test 52: login.html returns code 200
def test_code_200_pw_reset_req_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200

    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset_new Test 53: Happy path
def test_happy_path_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': 'test_password123',  # Using the original unhashed password as new password
        'password_confirmation': 'test_password123'
    }, follow_redirects=True)

    # Verify the response redirects to the login page
    assert response.request.path == '/login'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 54: User attempts to log in w/o valid CSRF token.
def test_missing_csrf_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': 'invalid_CSRF',
        'password': 'test_password123',  # Using the original unhashed password as new password
        'password_confirmation': 'test_password123'
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 55: Tests for presence of CSP headers in page.
def test_csp_headers_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': 'test_password123',  # Using the original unhashed password as new password
        'password_confirmation': 'test_password123'
    }, follow_redirects=True)

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None

    # Verify that the response is a redirect to the home page
    assert response.request.path == '/login'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /pw_reset/new Test 56: Invalid token- user submits invalid token via GET 
def test_bad_token_get_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token='invalid_token')

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 302
    
    # Verify that the response is a redirect to password_reset_request_new
    assert response.request.path == '/login'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 57: Missing value for pw_reset_new
def test_missing_pw_reset_new_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': ' ',  # Using the original unhashed password as new password
        'password_confirmation': 'test_password123'
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 58: Missing value for pw_reset_new_confirm
def test_missing_pw_reset_new_confirm_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': 'test_password123',
        'password_confirmation': ' '
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 59: Missing value for pw_reset_new and pw_reset_new_confirm
def test_missing_pw_reset_new_and_confirm_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': ' ',
        'password_confirmation': ' '
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 60: User enters insufficiently strong PW
def test_weak_new_pw_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': 'a',
        'password_confirmation': 'a'
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 61: Mismatching pw_reset_new and pw_reset_new_confirm
def test_missing_pw_new_and_missing_pw_new_confirm_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': 'test_password123',
        'password_confirmation': 'test_password1234'
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')


# /pw_reset/new Test 62: New password matches old password
def test_pw_new_pw_matches_old_pw_pw_reset_new(client, app):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    # Create a new test user
    test_user = insert_test_user_confirmed(client.application)
    
    # Mock the email sending function
    with patch('app.send_email') as mock_send:
        
        # Step 1: Get the CSRF token from the password reset request page
        response = client.get('/password_reset_request')
        assert response.status_code == 200

        html = response.data.decode()
        csrf_token_req = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

        # Step 2: User provided valid email address to /pw_reset_req
        response = client.post('/password_reset_request', data={
            'csrf_token': csrf_token_req,
            'email': test_user.email
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_send.assert_called_once()

    # Step 3: Generate a real token for the test user
    real_token = generate_real_token_for_test_user(test_user, app)

    # Step 4: User access pw_reset_new with a valid token
    with client.application.test_request_context():
        reset_url = url_for('password_reset_request_new', token=real_token)

    # Step 5: Get the CSRF token from the reset pag    
    get_response = client.get(reset_url)
    assert get_response.status_code == 200
    
    html = get_response.data.decode()
    csrf_token_reset = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    # Step 6: Submit the new password and confirmation    
    response = client.post(reset_url, data={
        'csrf_token': csrf_token_reset,
        'password': test_password_unhashed,
        'password_confirmation': test_password_unhashed
    }, follow_redirects=True)

    # Verify that the response is a redirect to password_reset_request_new
    decoded_token_url = unquote(reset_url)
    assert response.request.path == decoded_token_url
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: {test_number}... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /register_confirmation
# Summary: 
# Test 63: /register_confirmation Happy path


# Test 63: /register_confirmation Happy path
def test_happy_path_register_confirmation(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_unconfirmed(client.application)

    # Mock verify_reset_token to return the user_id of the created test user
    with patch('app.verify_unique_token') as mock_verify:
        mock_verify.return_value = {'id': test_user.id}

        with client.application.test_request_context():
            # Create the URL with a 'valid' token
            confirmation_url = url_for('register_confirmation', token='valid_token')
        
        # Simulate the GET request
        response = client.get(confirmation_url)

        # Verify that the response is a redirect (status code 302)
        assert response.status_code == 302

        # Generate the expected redirect URL
        with client.application.test_request_context():
            expected_url = url_for('index', _external=False)

        # Check that the response redirects to the index page
        assert expected_url in response.location
        clear_tables(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /buy
# Summary: 
# Test 64: buy.html returns code 200
# Test 65: Happy path
# Test 66: User attempts to submit w/o valid CSRF token.    
# Test 67: Tests for presence of CSP headers in page.
# Test 68: Missing value for symbol
# Test 69: Invalid value for symbol
# Test 70: Missing value for shares
# Test 71: Invalid value for shares
# Test 72: Insufficient cash for purchase


# /buy Test 64: returns code 200
def test_login_code_200_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 65: Happy path
def test_happy_path_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    
    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 66: User attempts to submit w/o valid CSRF token.
def test_missing_csrf_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... returned code 200')

    response = client.post('/buy', data={
        'csrf_token': 'invalid_token',
        'symbol': 'AAPL',
        'shares': '1',
    }, follow_redirects=True) 
    
    assert response.request.path == '/buy'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 67: Tests for presence of CSP headers in page.
def test_csp_headers_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None


# /buy Test 68: Missing value for symbol.
def test_missing_symbol_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)
    
    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': ' ',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/buy'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 69: Invalid value for symbol
def test_invalid_symbol_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'nmjhjkljn',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/buy'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 70: Missing value for shares
def test_missing_shares_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': ' ',
    }, follow_redirects=True)

    assert response.request.path == '/buy'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 71: Invalid value for shares
def test_invalid_shares_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 'shares',
    }, follow_redirects=True)

    assert response.request.path == '/buy'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /buy Test 72: Insufficient cash for purchase
def test_insufficient_cash_buy(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': '10000',
    }, follow_redirects=True)

    assert response.request.path == '/buy'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /sell
# Summary: 
# Test 73: sell.html returns code 200
# Test 74: Happy path
# Test 75: User attempts to submit w/o valid CSRF token.    
# Test 76: Tests for presence of CSP headers in page.
# Test 77: Missing value for symbol
# Test 78: Invalid value for symbol
# Test 79: User tries to sell symbol not already owned
# Test 80: Missing value for shares
# Test 81: Invalid value for shares
# Test 82: User tries to sell more shares than is owned


# /sell Test 73: returns code 200
def test_login_code_200_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 74: Happy path
def test_happy_path_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 75: User attempts to submit w/o valid CSRF token.
def test_missing_csrf_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... returned code 200')

    response = client.post('/sell', data={
        'csrf_token': 'invalid_token',
        'symbol': 'AAPL',
        'shares': '1',
    }, follow_redirects=True) 
    
    assert response.request.path == '/sell'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 76: Tests for presence of CSP headers in page.
def test_csp_headers_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None


# /sell Test 77: Missing value for symbol.
def test_missing_symbol_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': ' ',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/sell'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 78: Invalid value for symbol
def test_invalid_symbol_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': 'nmjhjkljn',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/sell'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 79: User tries to sell symbol not already owned
def test_symbol_not_owned_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': 'GS',
        'shares': 1,
    }, follow_redirects=True)

    assert response.request.path == '/sell'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 80: Missing value for shares
def test_missing_shares_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': ' ',
    }, follow_redirects=True)

    assert response.request.path == '/sell'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 81: Invalid value for shares
def test_invalid_shares_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 'shares',
    }, follow_redirects=True)

    assert response.request.path == '/sell'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /sell Test 82: Selling more shares than is owned
def test_more_shares_than_owned_sell(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')

    # Make a GET request to a page
    response = client.get('/buy')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/buy', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': 10,
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected')

    # Make a GET request to a page and check for status 200
    response = client.get('/sell')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/sell', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
        'shares': '11',
    }, follow_redirects=True)

    assert response.request.path == '/sell'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# ---------------------------------------------------------------------------------------------------------------
# Testing route: /quote
# Summary: 
# Test 83: quote.html returns code 200
# Test 84: Happy path
# Test 85: User attempts to submit w/o valid CSRF token.    
# Test 86: Tests for presence of CSP headers in page.
# Test 87: Missing value for symbol
# Test 88: Invalid value for symbol


# /quote Test 83: returns code 200
def test_login_code_200_quote(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/quote')
    assert response.status_code == 200
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /quote Test 74: Happy path
def test_happy_path_quote(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/quote')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/quote', data={
        'csrf_token': csrf_token,
        'symbol': 'AAPL',
    }, follow_redirects=True)

    # Check if response contains unique content from `quoted.html`
    assert 'Apple' in response.data.decode()

    print(f'{get_execution_order()} -- running test number: { test_number }... quoted.html rendered')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /quote Test 75: User attempts to submit w/o valid CSRF token.
def test_missing_csrf_quote(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
    
    # Make a GET request to a page and check for status 200
    response = client.get('/quote')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... returned code 200')

    response = client.post('/quote', data={
        'csrf_token': 'invalid_token',
        'symbol': 'AAPL',
    }, follow_redirects=True) 
    
    assert response.request.path == '/quote'
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /quote Test 76: Tests for presence of CSP headers in page.
def test_csp_headers_quote(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')
        
    # Make a GET request to a page and check for status 200
    response = client.get('/quote')
    assert response.status_code == 200

    # Check if CSP headers are set correctly in the response
    csp_header = response.headers.get('Content-Security-Policy')
    assert csp_header is not None


# /quote Test 77: Missing value for symbol.
def test_missing_symbol_quote(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)

    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')

    # Make a GET request to a page and check for status 200
    response = client.get('/quote')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/quote', data={
        'csrf_token': csrf_token,
        'symbol': ' ',
    }, follow_redirects=True)

    assert response.request.path == '/quote'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /quote Test 78: Invalid value for symbol
def test_invalid_symbol_quote(client):
    global test_number
    test_number += 1
    print(f'{get_execution_order()} -- running test number: { test_number }... test started')

    test_user = insert_test_user_confirmed(client.application)
    if not test_user:
        print(f'{get_execution_order()} -- running test number: { test_number }... failed to generate test_user')
        return

    response = client.get('/login')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/login', data={
        'csrf_token': csrf_token,
        'email': test_user.email,
        'password': test_password_unhashed
    }, follow_redirects=True)
    assert response.request.path == '/'
    print(f'{get_execution_order()} -- running test number: { test_number }... successfully logged in test_user')

    # Make a GET request to a page and check for status 200
    response = client.get('/quote')
    assert response.status_code == 200
    print(f'{get_execution_order()} -- running test number: { test_number }... status code is 200')
    
    html = response.data.decode()
    csrf_token = re.search('name="csrf_token" type="hidden" value="(.+?)"', html).group(1)

    response = client.post('/quote', data={
        'csrf_token': csrf_token,
        'symbol': 'nmjhjkljn',
    }, follow_redirects=True)

    assert response.request.path == '/quote'
    print(f'{get_execution_order()} -- running test number: { test_number }... user redirected to /login')
    
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')
