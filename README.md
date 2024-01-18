# MyFinance50 - A CS50 Finance-inspired mock brokerage web app
### Video Demo:  XX LINK HERE XX

### Description:
- MyFinance50 is a web application that simulates a brokerage account, with real-time market data provided via the Yahoo Finance api.
- MyFinance50 is inspired by CS50's Finance, with significant additional functionality and security.
- This project was completed as the final project for [Harvard's CS50p 2022](https://cs50.harvard.edu/python/2022/)
- Assignment was submitted on: XX DATE HERE XX


#### Motivation for project:
This project is a tribute to [Harvard University's CS50x](https://cs50.harvard.edu/) week 9 assignment: Finance. For that assignment, students are tasked with building a basic mock brokerage account with Python/Flask. 

This project takes the same task and extends it significantly, upgrading security, modularity, and the degree of analysis made available to the user.


#### Key elements:
1. This project features key elements of a brokerage account, including: 
    - User sign-up, including registration confirmation link sent via email
    - Customizable input validation
    - Password reset (via unique link sent via email) and password change
    - User profile management by user

1. Languages used:
    - Front-end: HTML / JavaScript (using Bootstrap 5 w/ minor CSS customizations) / Jinja / Flask-WTF
    - Back-end: Python / Flask / Flask-WTF
    - Datbase: sqlite3 (managed via SQLAlchemy OOM)
    - Environment: Uses custom virtual environment

1. Significant focus on security:
    - All SQL inputs are automatically parameterized via use of SQLAlchemy to protect against SQL injection attacks
    - Use of jinja to pass user-inputted elements to HTML to protect against HTML injection attacks
    - User input is checked against whitelisted chars to protect against SQL, HTML, XSS, and other attacks
    - Use of customized Content Security Policy (CSP) managed by Flask Talisman to protect against cross-site scripting (XSS), clickjacking and other code injection attacks
    - Use of CSRFProtect to protect against cross-site registry attacks
    - Use of cryptographic tokens sent to the user via email as part of 2-step registration and password reset processes
    - Exclusion of sensitive data (e.g. passwords) from being stored in Session or in cryptographic token used for password reset
    - Externalization of sensitive data (e.g. login needed to send emails programmatically) to .env file
    - Exclusion of .env file and other sensitive data from upload to GitHub via .gitignore file
    - Daily (12pm GST) automated purging of stale, unconfirmed user accounts via a cron job



#### KEY FEATURES:
1. Use of database to store user data
    - See: finance.sqlite

1. User creation/registration
    - See: app.py --> /register
    - See: register.html
    - User input is validated before submission
    - Username availability and satisfaction of password requirements is communicated to the user real-time via JavaScript
    - Registration button is only enabled after user has provided valid inputs to all required fields.
    - Successful validation and submission of registration form via Flask-WTF classes using custom validators and filters:
        -The user's data is entered into the database, with the user's confirmed status = False
        -The app then automatically generates a cryptographic token and sends that token to the email address provided by the user
        - The user must then click on the link the email sent to them by the application. That link directs the user back to the application, at which time their account's status is changed to 'confirmed' in the database, allowing for login and access to the application.

1. Extensive user input validation and password management
    - See: app.py
    - Standard and custom Flask-WTF filters and validators, including [Custom_FlaskWtf_Filters_and_Validators](https://github.com/TheBuleGanteng/Custom_FlaskWtf_Filters_and_Validators). All forms display helpful error messages  alongside the form fields that failed validation.
    - Fully customizable parameters for password strength (min password length, min letters, min chars, min symbols, prohibited symbols).
    
1. Use of JavaScript to provide validation feedback to users, make input fields appear/disappear, and enable/disable submit button
    - See: app.py --> /buy, /profile, /register,  /sell
    - See: buy.html, profile.html, register.html, sell.html
    - Clicking button makes input fields appear/disappear based on onclick() listener (profile.html).
    - Inputting data triggers real-time feedback to user about username availability and password validation.
    - Inputting of all required data makes enabled submit button appear (done via promise chain).

1. Account management for existing users
    - See: app.py --> /register, /pw_change, pw_reset_req, /pw_reset_new/<token>
    - Password change (for users already logged in)
    - Password reset via cryptographic token + email link (for users not logged in)

1. Preserves flash messages and CSRF token stored in Session, even in routes where Session is cleared to enforce user to be logged out (e.g. /password reset, /register)
    - See app.py
    - Stores Session data to be preserved in a temporary variable before Session is cleared, allowing that data to be used later in the route

1. Connection to gmail for programmatic email generation (including 
password reset emails)
    - See app.py --> /pw_reset_req and /register

1. Use of CronJob to automatically remove users who have not confirmed their registration and whose token has expired

1. Use of url_for throughout
    - See: various app.py (all redirects) and htmls (all <a> links)
    - Makes links more maintainable, enables Blueprints

1. Navbar contents are dynamic based on whether user is logged in
    - See: layout.html
    - Uses jinja to alter display of navbar elements relative to whether user
    is already logged in

1. Extensive user profile management for users logged in
    - See app.py --> /profile
    - See profile.html
    - Ability for logged-in user to update their username, first and last name, 
    birthdate, gender, etc.
    
1. Use of a cool favicon :-0


#### NOTES FOR USE:
This project uses a submodule of the [Custom_FlaskWtf_Filters_and_Validators](https://github.com/TheBuleGanteng/Custom_FlaskWtf_Filters_and_Validators) repository. To ensure you are using the most updated version of that repository, please do the following upon download:

1. Navigate to the Submodule Directory within your main project.
*cd path/to/Custom_FlaskWtf_Filters_and_Validators*

1. Pull the Latest Changes: Fetch and check out the latest changes from the remote repository of the submodule. Replace 'master' with the branch you wish to pull from, if different
*git pull origin master*  

1. Commit the Submodule Update in the Main Project: Go back to the root directory of your main project and commit the changes. This step updates the main project to point to the new commit of the submodule.
*cd ../..*  # Adjust this path to get back to your main project root
*git add path/to/Custom_FlaskWtf_Filters_and_Validators*
*git commit -m "Update Custom_FlaskWtf_Filters_and_Validators submodule"*

1. Push the Changes: Push the changes to your main project's remote repository.
*git push*

1. Update Other Copies: If there are other copies of your main project (like on other developers' machines or different environments), you need to update the submodule there as well:
*git pull*  # In the main project directory
*git submodule update --init --recursive*

This process ensures that your main project uses the specific, updated version of the Custom_FlaskWtf_Filters_and_Validators submodule.