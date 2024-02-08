from app import create_app, db as test_db
from configs.config_testing import TestingConfig
from datetime import date
from models import User, Transaction
import pytest
import re
from unittest.mock import patch, MagicMock
import uuid
from werkzeug.security import generate_password_hash



# Setup steps summary: 
# Setup step 1: Creates instance of app and test DB, awaits tests, and then tears down
# Setup step 2: Creates virtual CLI used to execute tests
# Setup step 3: Creates a timestamp that can be added to print statements to aid debugging
# Setup step 4: Declare global variable for test number
# Setup step 5: Create an instance of app.py for testing.
# Setup step 6: Defines function to clear the users table
# Setup step 7: Defines function to CREATE an UNCONFIRMED test user
# Setup step 8: Defines function to CREATE a CONFIRMED test user
# Setup step 9: Defines function to DELETE an UNCONFIRMED test user
# Setup step 10: Defines function to DELETE a CONFIRMED test user


# Setup step 1: Create instance of app w/ testing config, create test DB, wait for tests 
# to complete, and then delete test DB from memory.
@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        test_db.create_all()
        yield app  # This is where the testing happens!
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


# Setup step 7: Defines function to CREATE an UNCONFIRMED test user in the DB where confirmed = 0
def insert_test_user_unconfirmed(test_app):
    with test_app.app_context():
        test_user_email = f'{uuid.uuid4()}@mattmcdonnell.net'
        test_password_unhashed = 'GLBMjKJ3qphUodwvqyF!+-='
        test_password_hashed = generate_password_hash(test_password_unhashed)
        test_user = User(
            name_first='Pytest_Name_First',
            name_last='Pytest_Name_Last',
            username='PytestUser',
            email=test_user_email,
            confirmed='No',
            created='2024-01-01 00:00:00.000000',
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
        user_data_unconfirmed_user = User.query.filter_by(user_email=test_user_email).first()
        if user_data_unconfirmed_user:
            user_data_unconfirmed_user.pw_unhashed = test_password_unhashed
            print(f'{get_execution_order()} -- running insert_test_user_unconfirmed(app)... user_data_unconfirmed_user is: { user_data_unconfirmed_user }')
            return user_data_unconfirmed_user
        else:
            print(f'{get_execution_order()} -- running insert_test_user_unconfirmed(app)... no user_data_unconfirmed_user created')
            return None


#Setup step 8: Defines function to CREATE a CONFIRMED test user in the DB
def insert_test_user_confirmed(test_app):
    with test_app.app_context():
        test_user_email = f'{uuid.uuid4()}@mattmcdonnell.net'
        test_password_unhashed = 'GLBMjKJ3qphUodwvqyF!+-='
        test_password_hashed = generate_password_hash(test_password_unhashed)
        test_user = User(
            name_first='Pytest_Name_First',
            name_last='Pytest_Name_Last',
            username='PytestUser',
            email=test_user_email,
            confirmed='Yes',
            created='2024-01-01 00:00:00.000000',
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
        user_data_test_user = User.query.filter_by(user_email=test_user_email).first()
        if user_data_test_user:
            user_data_test_user.pw_unhashed = test_password_unhashed
            print(f'{get_execution_order()} -- running insert_test_user_confirmed(app)... user_data_test_user is: { user_data_test_user }')
            return user_data_test_user
        else:
            print(f'{get_execution_order()} -- running insert_test_user_confirmed(app)... no user_data_test_user created')
            return None


# Setup step 9: Defines function to DELETE the UNCONFIRMED test user
def delete_test_user_unconfirmed(user_email, test_app):
    with test_app.app_context():
        user_data_unconfirmed_user = User.query.filter_by(user_email=user_email).first()
        if user_data_unconfirmed_user:
            print(f'{get_execution_order()} -- running delete_test_user_unconfirmed(user_email, app)... user_data_unconfirmed_user is: { user_data_unconfirmed_user }')
            test_db.session.delete(user_data_unconfirmed_user)
            test_db.session.commit()
            print(f'{get_execution_order()} -- running delete_test_user_unconfirmed(user_email, app)... user_data_unconfirmed_user deleted from session')
        else:
            print(f'{get_execution_order()} -- running delete_test_user_unconfirmed(user_email)... no user_data_unconfirmed_user found in DB.')


# Setup step 10: Defines function to DELETE the CONFIRMED test test user
def delete_test_user_confirmed(user_email,test_app):
    with test_app.app_context():
        user_data_test_user = User.query.filter_by(user_email=user_email).first()
        if user_data_test_user:
            print(f'{get_execution_order()} -- running delete_test_user_confirmed(user_email, app)... user_data_test_user is: { user_data_test_user }')
            test_db.session.delete(user_data_test_user)
            test_db.session.commit()
            print(f'{get_execution_order()} -- running delete_test_user_confirmed(user_email, app)... user_data_test_user deleted from session')
        else:
            print(f'{get_execution_order()} -- running delete_test_user_confirmed(user_email)... no user_data_test_user found in DB.')
     


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
def test_login_code_200(client):
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
def test_login_happy_path(client):
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
        'user_email': test_user.user_email,
        'password': test_user.pw_unhashed
    }, follow_redirects=True)

    assert response.request.path == '/'
    clear_tables(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 3: User attempts to log in w/o valid CSRF token.
def test_login_missing_CSRF(client):
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
        'user_email': test_user.email,
        'password': test_user.unhashed
    }, follow_redirects=True)

    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 4: Tests for presence of CSP headers in page.
def test_login_csp_headers(client):
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
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 5: User does not submit email address
def test_login_without_email(client):
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
        'user_email': '',
        'password': test_user.unhashed
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 6: User does not submit PW
def test_login_without_pw(client):
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
        'user_email': test_user.email,
        'password': '',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 7: User does not submit username or password  --> is redirected 
# to /login and flashed message.
def test_login_without_email_without_pw(client):
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
        'user_email': '',
        'password': '',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')


# /login Test 8: User enters undeliverable email address.
def test_login_undeliverable_email(client):
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
        'user_email': 'matt',
        'password': test_user.unhashed,
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 9: User tries to log in w/ unregistered email address + correct PW
def test_login_with_unregistered_email(client):
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
        'user_email': 'unregistered@mattmcdonnell.net',
        'password': test_user.unhashed,
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 10: User tries to log in w/ registered email address + invalid PW
def test_login_with_invalid_pw(client):
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
        'user_email': test_user.email,
        'password': 'InvalidPassword',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 11: User tries to log in w/ unregistered email address + invalid PW
def test_login_with_invalid_username_invalid_pw(client):
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
        'user_email': 'unregistered@mattmcdonnell.net',
        'password': 'InvalidPassword',
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')



# /login Test 12: User tries to log in w/ unconfirmed account
def test_login_for_unconfirmed_user(client):
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
        'user_email': test_user.email,
        'password': test_user.unhashed,
    }, follow_redirects=True)
    
    # Check if redirected to the login page
    assert response.request.path == '/login'
    clear_users_table(client.application)
    print(f'{get_execution_order()} -- running test number: { test_number }... test completed')




# ---------------------------------------------------------------------------------------------------------------
# Testing route: /register
# Summary: 
# Test 13: login.html returns code 200
# Test 14: Happy path, scenario a (all fields, valid email, username, pw)
# Test 15: Happy path, scenario a (all fields, valid email, username, pw)
# Test 16: Happy path, scenario b (all required fields, valid email, username, pw)
# Test 17: User attempts to log in w/o valid CSRF token.
# Test 18: No CSP headers in page
# Test 19: Missing req. field: email address
# Test 20: Missing req. field: username
# Test 21: Missing req. field: password
# Test 22: Missing req. field: password confirmation
# Test 23: Password fails strength test (uses pw = 'a' for test) 
# Test 24: PW =! PW confirmation 
# Test 25: User enters illegitimate email address.
# Test 26: User enters prohibited char in any user inputs (using '>' as test)
# Test 27: User enters an already-registered username.
# Test 28: User enters an already-registered email address.
   

# /login Test 13: register.html returns code 200
def test_login_code_200_register(client):
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


# /register Test 14: Happy path, scenario a (all fields, valid email, username, pw) --> user redirected to /index w/ success 
def test_register_happy_path_part_a(client):
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
        clear_users_table(client.application)
        print(f'{get_execution_order()} -- running test number: { test_number }... test completed')