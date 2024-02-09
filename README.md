# MyFinance50 - A CS50 Finance-inspired mock brokerage web app
### Video Demo:  XX LINK HERE XX

### Description:
- MyFinance50 is a web application that simulates a brokerage account, with real-time market data provided via the Yahoo Finance api.
- MyFinance50 is inspired by CS50's Finance, with use of a new [API](https://site.financialmodelingprep.com/developer/docs), significant additional functionality, and greater security.
- This project was completed as the final project for [Harvard's CS50p 2022](https://cs50.harvard.edu/python/2022/)
- Assignment was submitted on: XX DATE HERE XX


#### Motivation for project:
This project is a tribute to [Harvard University's CS50x](https://cs50.harvard.edu/) week 9 assignment: Finance. For that assignment, students are tasked with building a basic mock brokerage account with Python/Flask. 

This project starts with that task and extends it significantly, upgrading functionality, modularity, UI/UX security, and the depth of financial analysis made available to the user.


#### Key elements:
1. This project features key elements of a brokerage account, including: 
    - User sign-up, including registration confirmation link sent via email
    
1. User registration
    - Two-stage user registration in which a user completes all fields and upon submit, the user's status is set to unconfirmed and the user is sent an email with a cryptographic registration confirmation link.
    - When the user clicks the registration confirmation link, the user's account status is updated to confirmed and the user is now able to log in and use the app.
    - Unconfirmed accounts over a threshold age are automatically purged from the database.

1. Customizable user profile, including accounting and tax settings
    - Updatable profile for name, username
    - Updatable settings for key accounting and tax metrics, such as LIFO/FIFO, capital loss tax offsets, short-term capital gains tax rates, and long-term capital gains tax rates.
    - Live validation to the user for username availability 
    - Submit button is enabled only when valid inputs are detected

1. Password change
    - In-app password change using user email address and current password as validators

1. Password reset
    - Two-stage password reset in which the user provides his or her email, is automatically sent an email with a cryptograpic password reset link, and once the user clicks the link, the app validates the link and allows the user to reset his or her password.
    - Cryptographic link is time-bound for increased security.

1. Index:
    - Index view provides the user with an in-depth view of the user's current portfolio of open positions and cash, including before- and after-tax returns.
    - User can see additional information about the stocks in their portfolio by clicking on any ticker, which redirects the user to that company's corporate profile page via the '/quote' route.
    - Market prices are live and refreshed upon page reload, using the [FMP API}(https://site.financialmodelingprep.com/developer/docs)

1. Detailed index:
    - A more granular view of the user's current portfolio of open positions, cash, and previous share sales, broken down by cost basis, current market value, short- and long-term capital gains, short- and long-term capital gains tax, capital loss tax offsets, and before and after-tax returns.
    - User can see additional information about the stocks in their portfolio by clicking on any ticker, which redirects the user to that company's corporate profile page via the '/quote' route.
    - Market prices are live and refreshed upon page reload, using the [FMP API}(https://site.financialmodelingprep.com/developer/docs)

1. Buy:
    - Allows user to 'buy' shares in any of the ~7,000 companies available via the FMP API.
    - User input for stock symbol is checked in real-time against a database record of companies downloaded from the FMP API daily and provides real-time autocomplete capabilities, allowing the user to search by company symbol or name.
    - Once the user has inputted a valid share symbol and a number of shares to be purchased, the user is provided with real-time feedback regarding his or her cash on hand, the cost of the proposed share purchase, and whether cash on hand is sufficient to cover the proposed purchase.
    - Only after valid inputs for symbol and number of shares is detected, the submit button is enabled.
    - The symbol, number of shares, and market price of the company are again validated on the back-end before the database is updated to adjust the transactions table and user table to reflect the new purchase transaction and the reduction in user's cash.

1. Sell:
    - Allows user to 'sell' shares currently 'owned'.
    - User selects company in which he or she wishes to sell shares from the list of companies in teh user's current portfolio.
    - One the user has inputted the number of shares he or she wishes to sell, the user is provided with real-time feedback regarding whether he or she owns sufficient shares to cover the proposed sale.
    - Only after valid inputs for symbol and number of shares is detected, the submit button is enabled.
    - The symbol, number of shares, and market price of the company are again validated on the back-end before the database is updated to adjust the transactions table and user table to reflect the new sale transaction and the increase in user's cash.
    
1. Quote:
    - Allows user to view in-depth real-time information regarding companies.
    - User input for stock symbol is checked in real-time against a database record of companies downloaded from the FMP API daily and provides real-time autocomplete capabilities, allowing the user to search by company symbol or name.
    - Only after valid input for symbol is detected, the submit button is enabled.
    - Upon submit of a valid symbol, the user is redirected to the company profile corresponding to that symbol, including the company's stock price, daily change, beta, 52-week price range, company description, industry, etc.







#### UNDER THE HOOD:

1. Languages used:
    - Front-end: HTML / JavaScript incl. AJAX for live search and autocomplete / [Bootstrap5](https://getbootstrap.com/docs/5.0/getting-started/introduction/) CSS w/ minor  customizations / [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) / [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.2.x/)
    - Back-end: Python / Flask / Flask-WTF
    - Datbase: sqlite3 (managed via [SQLAlchemy](https://www.sqlalchemy.org/) OOM)
    - Environment: Uses custom virtual environment

1. Significant focus on security:
    - All SQL inputs are automatically parameterized via use of SQLAlchemy to protect against SQL injection attacks
    - Use of jinja to pass user-inputted elements to HTML to protect against HTML injection attacks
    - User input is checked against whitelisted chars to protect against SQL, HTML, XSS, and other attacks
    - Use of customized Content Security Policy (CSP) managed by Flask Talisman to protect against cross-site scripting (XSS), clickjacking and other code injection attacks
    - Use of CSRFProtect to protect against cross-site registry attacks
    - Use of cryptographic tokens sent to the user via email as part of 2-step registration and password reset processes
    - Secondary back-end validation of all user submissions.
    - Exclusion of sensitive data (e.g. passwords) from being stored in Session or in cryptographic token used for password reset
    - Externalization of sensitive data (e.g. login needed to send emails programmatically) to .env file
    - Exclusion of .env file and other sensitive data from upload to GitHub via .gitignore file
    - Daily (12pm GST) automated purging of stale, unconfirmed user accounts via a cron job


1. Connection to gmail via source credentials for secure programmatic email generation (including 
password reset emails)

1. Use of CronJobs to automatically run scripts for purging unconfirmed users, emailing logs, and updating the database list of companies.



#### NOTES FOR USE:

##### Updating Custom_FlaskWtf_Filters_and_Validators
This project uses a submodule of the [Custom_FlaskWtf_Filters_and_Validators](https://github.com/TheBuleGanteng/Custom_FlaskWtf_Filters_and_Validators) repository. To ensure you are using the most updated version of that repository, please do the following upon download:

1. Navigate to the Submodule Directory within your main project.
*cd path_to_your_project_folder/Custom_FlaskWtf_Filters_and_Validators*

1. Update Submodule: Run the following command to fetch and update the submodule to the latest commit from the remote repository.
*git submodule update --remote Custom_FlaskWtf_Filters_and_Validators*

1. Review Changes: Check the changes fetched from the submodule to ensure they are what you expect. You should see that the Custom_FlaskWtf_Filters_and_Validators submodule has new commits.
*git status*

1. Commit the Submodule Update: Commit the submodule update in your main project to record the change in which commit the submodule is pointing to.
*git add Custom_FlaskWtf_Filters_and_Validators*
*git commit -m "Update Custom_FlaskWtf_Filters_and_Validators submodule to latest"*

1. Push Changes: Push the update to your remote repository.
*git push*

This process ensures that your main project uses the specific, updated version of the Custom_FlaskWtf_Filters_and_Validators submodule.

##### Models.py
This project uses [SQLAlchemy ORM](https://www.sqlalchemy.org/) to manage database interactions. Instructions for updating models.py is as follows:

1. Migrate via the following command:
*flask db migrate -m "Description of the changes"*
