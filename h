[33mcommit 19bafba6efe7ddae9cfadd419d1a9abb0677d816[m[33m ([m[1;36mHEAD -> [m[1;32mmain[m[33m)[m
Author: thebuleganteng <mcdonnell.matthew@ymail.com>
Date:   Mon Feb 5 13:31:14 2024 +0700

    Remove Custom_FlaskWtf_Filters_and_Validators submodule

[33mcommit ce2eb3e34900773718478d1a75867140bf8dc895[m[33m ([m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m
Author: thebuleganteng <mcdonnell.matthew@ymail.com>
Date:   Mon Feb 5 13:27:53 2024 +0700

    MF50: Updating .girmodules for proper file path

[33mcommit 3b1ce6e124adc6cb6297fdb85a9e81fe70121b02[m
Author: thebuleganteng <mcdonnell.matthew@ymail.com>
Date:   Mon Feb 5 13:21:06 2024 +0700

    Update submodule path and configuration

[33mcommit fac5d69efb2d27574801cae40cec89c390ee5e30[m
Author: thebuleganteng <mcdonnell.matthew@ymail.com>
Date:   Mon Feb 5 12:38:56 2024 +0700

    MF50: Updated index and detailed index pages, windowing of history by date and txn type
    
    1. app.py -> /index /index_detail, index.html, index_detail.html: improved computation of portfolio composition and performance, including cap gains type (ST or LT) cap gains tax type (ST vs LT) and amount by type, and after-tax returns
    2. app.py --> /history and history.html: Including windowing by transaction type and transaction date.
    3. index.html, index_detail.html, history.html: made tables responsive using bootstrap
    4. quote.html: minor cosmetic updates
    5. /helpers: relocated helpers.py to folder and factored out profile object creation to its own profile.py file. Using both with __init__.py to create a package for simpler importing to app.py

[33mcommit cd41c41e49d20756d3e658fdddbf000f3be2a1a7[m
Author: thebuleganteng <mcdonnell.matthew@ymail.com>
Date:   Tue Jan 30 13:07:39 2024 +0700

    MYF50:
    1. helpers.py: Added user's STCG, LTCG, and tax_loss settings to construction of portfolio
    2. finance.sqlite: Added shares_outstanding col to database
    4. app.py: updated /buy to include shares_outstanding
    5. app.py, helpers.py: updated sell to use process_sale()

[33mcommit 4783bb55dddd490f80ccbc061b6a408cd452eb7e[m
Author: thebuleganteng <mcdonnell.matthew@ymail.com>
Date:   Mon Jan 29 17:04:02 2024 +0700

    MF50:
    1. MF50.js: elimianted double api calls from /sell

[33mcommit 9bdb3809845849cf890277f90691a9dd87e5dde4[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Mon Jan 29 11:21:33 2024 +0700

    MF50:
    1. listings_update.py,  listings_unconfirmed.log: fixed cron job issues
    2. purge_unconfirmed.py, purge_unconfirmed.log, crontab: Set up daily 2am cron job to purge unconfirmed accounts
    3. Updated nano ~/.bashrc to give me execute permissions for new scripts by default
    4. Helpers.py: Added daily API ping counter

[33mcommit 4ada295286df2804ee02b779ec35583cac852c61[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sun Jan 28 19:16:21 2024 +0700

    MF50- forgot to save prior to last push

[33mcommit 6d3789f759f9c1b28ec680f0f958ef303c064858[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sat Jan 27 20:39:24 2024 +0700

    -

[33mcommit 8042000f5a13ddac3c64a0302c4c07ee2a109b46[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sat Jan 27 20:36:08 2024 +0700

    MF50:
    1. app.py: Updating argument for txn type in /buy and /sell
    2. MF50.js: Eliminated double API pings JS validation for /buy

[33mcommit 7a2a1cd7ffc507288c064037ac645de39aeb65b6[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sat Jan 27 15:28:55 2024 +0700

    -

[33mcommit 4307fc9730bb56b3ed9bd262eb46169b37657b35[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sat Jan 27 15:26:40 2024 +0700

    MF50:
    1. app.py, extensions.py: factored out extension initiation to reduce circular imports
    2. Models.py, finance.sqlite: Added listings table to store list of tickers from api
    3. myFinance50_helpers.py: renamed from helpers.py due to conflicts
    4. /scripts/listings_update.py: Added script to run with cron job daily at 2am. Also deleted legacy cron job.

[33mcommit 28df446953d6d1af1f3462ad68272b563befbbe3[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Fri Jan 26 11:29:05 2024 +0700

    MF50F: helpers.py, app.py: .env: Migrated away from STMP for email sending

[33mcommit ee74d5fae7f30ee808b2f20304fe6eb04743f351[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Tue Jan 23 20:57:29 2024 +0700

    MF50- app.py: fixed calc to make total txn value negative if running /sell

[33mcommit b919728d2980d4f506632ca729dc6cb3cc34c854[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Tue Jan 23 20:27:49 2024 +0700

    MF50:
    1. app.py: updated /check_valid_shares, /buy, /sell for new buy vs sell framework w/ hidden transaction_type tags
    2. forms.py: added hidden transaction_type tags to BuyForm and SellForm
    3. MF50.js: updated jsSharesValidation and all enableSubmitButtons to accommodate hidden transaction_type tags and to disable submit while promises are WIP

[33mcommit 27fc0681bec34c1e73d598a1ae001bfbe6d2e982[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Mon Jan 22 18:24:27 2024 +0700

    MF50: profile.html, myFinance50.js, forms.py, models.py, app.py, register.html, profile.html: Updated DB, routes, html, and js to allow for user input for accounting treatment(LIFO/FIFO), tax loss netting (Yes/No), ST cap gains tax rate, and LT cap gains tax rate

[33mcommit 153d6a1d1022b426cbce21f93fb3fd1d5ff893ce[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Fri Jan 19 19:37:35 2024 +0700

    MF50: app.py: updated for 2-stage registration w/ confirmation link via email

[33mcommit 089130644dcaf332792dabb7666ecf6599c2b137[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Fri Jan 19 14:23:49 2024 +0700

    MF50:
    1. app.py: created password_reset_request and password_reset_request routes to enable 2-stage password reset
    2. password_reset_request.html, password_reset_request_new.html: created
    3. MF50: Updated for password_reset_request.html and password_reset_request_new.html validation

[33mcommit 76616b9fbfe447976860463a31473623ee960e94[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Fri Jan 19 08:59:06 2024 +0700

    MF50:
    1. app.py: resolved issue w/ naming of vars in /password_change
    2. register.html, profile.html, password_change.html, register.html: Removed container holding form to left-align form w/ instructions

[33mcommit 5f46ce4cefa4957f92d6571b1005a1f8d299effa[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Fri Jan 19 07:43:06 2024 +0700

    MF50:
    1. app.py, forms.py, .env: adjusted file path for generic forms and validators
    2. register.html, password_change.html: updated html so error is below user input
    3. register.html, profile.html: Updated instructional text
    4. profile.htm: added cancel, submit buttons

[33mcommit 62e61e144671b64c95e886d5a9a6b4fe13b51771[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Thu Jan 18 18:52:45 2024 +0700

    MF50: readme.md: correction to git pull instructions

[33mcommit 260576b162aa84f021f334d1e2bcec43d09969da[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Thu Jan 18 18:47:08 2024 +0700

    MF50: myFinance50.js: username, email, pw, pw_confirmation validation JS all working
    app.py: updated checks to work internally and with JS

[33mcommit 827c4a7aea5a177ffdaa4a5e6953d0642ba0c172[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Thu Jan 18 18:43:46 2024 +0700

    MF50: myFinance50.js: username, email, pw, pw_confirmation validation JS all working
    app.py: updated checks to work internally and with JS

[33mcommit b2a0d24bfef7c3a4e1145241e9b201a96b6fedcd[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Thu Jan 18 11:34:45 2024 +0700

    MF50: app.py: Added csp, relative file path for cloned custom flask-wtf, added /profile route; myFinance50.js: created and added functions for profile and nonces; config files: added path to .env for custom flask-wtf; .env: added path for custom flask-wtf

[33mcommit 8c0362ae613119de60ec236da9e33df0efebc42f[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Thu Jan 18 11:11:37 2024 +0700

    Added Custom_FlaskWtf_Filters_and_Validators submodule

[33mcommit 53cb61b059059c3921f45b772f538799f3c17cd8[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Jan 17 01:41:51 2024 +0700

    MF50: app fully converted for SQLAlchemy + Flask-WTF

[33mcommit d3f3f7ff38da72b70bc060bb65400a40fc21cea6[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Tue Jan 16 10:05:27 2024 +0700

    MF50: models.py: added, .env: added, settings.py files: added, completely transitioned to SQLAlchemy

[33mcommit 15eb0ba1222ae9d8fae349d53d10aad8bb2aac27[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sat Jan 13 16:25:53 2024 +0700

    MF50- Updated to use virtual environ

[33mcommit d7eab661d078bfdce2e949eb10f2c59b2ab9dcef[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Sat Jan 13 15:52:00 2024 +0700

    MF50- repository name change

[33mcommit d239ef0ebb18ad18b3a1e12502400835c6a9377c[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Mon Sep 18 14:07:41 2023 +0700

    app.yaml: changed instances 4->1

[33mcommit 8dd841a5029faf42f5c05c99f3a032fcd8530397[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 17:44:37 2023 +0700

    login.html: -fixed typo :-/

[33mcommit 4bc79303b46a6d886f0997ea4b0d55b4496421b5[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 17:40:18 2023 +0700

    login.html: - Added link to create account

[33mcommit 9895ba3f9ce94c05f5ec6640937ee373a2ec287b[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 16:28:58 2023 +0700

    req.txt: -added gunicorn

[33mcommit 56e511899e7d094097d9e2386022e5b8c88dbebb[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 16:26:22 2023 +0700

    adding gunicorn per chatgtp  changed port to 8080

[33mcommit db3a6057108b12a2b8df575c3b8a97b8ff85ab60[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 16:16:48 2023 +0700

    app.py: -updated app.run()

[33mcommit f815446e115fe4995cd5f291f613924832ef1da0[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 16:04:01 2023 +0700

    app.py: -removing pytz

[33mcommit 255d200ec568374460c493b41a1e43f98ed2ca18[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 16:00:56 2023 +0700

    removing pytz from helpers.py

[33mcommit 7531de48b40b1c67b1001729ed68607ddb8817cf[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:59:44 2023 +0700

    --

[33mcommit 88e3b4f288e37862a9f7990312df9e6ab0d69b80[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:50:48 2023 +0700

    --

[33mcommit f6185c4f3dac94a1e2f07b784a125fa10bee5c71[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:45:50 2023 +0700

    --

[33mcommit 1a61632be5f839791e59e7bc47c4f32c1cdb6560[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:45:15 2023 +0700

    app.py: -added port=port

[33mcommit 03e1e1a7d3b652992b7fbe2affcc89df7afdc511[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:40:29 2023 +0700

    --

[33mcommit 26d36173e45de212f305b7c5d60bba4ccd18caef[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:36:28 2023 +0700

    re-downloading from cs50

[33mcommit eea5f5588351ec03f3df4ba28fa4b450287cd5c6[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:11:21 2023 +0700

    Delete .env

[33mcommit 0fe0a82f5f329a42e5d76b0178f4293522d30a02[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:11:10 2023 +0700

    Delete finance.db

[33mcommit 7ab9173933094e6878aa4f7c7c989e916ead00c5[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:11:01 2023 +0700

    Delete requirements.txt

[33mcommit b92b4c3a2234325e043e91d238d5c6aa7f4e0226[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:10:47 2023 +0700

    Delete helpers.py

[33mcommit a220a0c4e339431b1ad53b868004c73b3d8499b5[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:10:01 2023 +0700

    Delete app.py

[33mcommit 8c0a6d43c91bd0de2d4453b78e628d3fd73b5d2c[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:09:38 2023 +0700

    Delete README.md

[33mcommit 72999e12ff456d5488a73295a81dc591c8ef5635[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:09:11 2023 +0700

    Delete templates directory

[33mcommit 6595e2c4062ff8b2d669ea839d234e236eff90da[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Thu Sep 14 14:08:47 2023 +0700

    Delete static directory

[33mcommit cfe7da6dd59c6dbb1d09217b39cc9f7642b5a731[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:23:56 2023 +0700

    --

[33mcommit 5b07d6896d64c17c708fd22ec2a76f2c3b689e14[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 15:23:40 2023 +0700

    Revert "now using venv"
    
    This reverts commit 0f43d6f52efd2bfd2486b16ddd2162ba0a9c9c1e.

[33mcommit 0f43d6f52efd2bfd2486b16ddd2162ba0a9c9c1e[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 14:52:46 2023 +0700

    now using venv

[33mcommit 8bc9b3be5f5fbe5036f33086821226e40f2eedef[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 13:52:01 2023 +0700

    .env: -Adding env file to store PORT=5000

[33mcommit b3f804401b407ebec7d33647a8aaaf1fcbf9f4c9[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 13:39:07 2023 +0700

    app.py: -restored environ var

[33mcommit 130a503396997547be070e49b2e02efacb8255cb[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 13:32:05 2023 +0700

    app.py: - set port to static=10000

[33mcommit 42f2c69ab706358c0c360c57f315847006eb8791[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 13:16:07 2023 +0700

    --

[33mcommit 7da696be2cf5316cdd5ea445995559c06804f6e7[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 13:07:59 2023 +0700

    app.py: -adding envion variable for port

[33mcommit 3571415a378a811b08a54756d54b2053c9cde8e2[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 13:03:19 2023 +0700

    app.py: -adding app.run to address no port issue

[33mcommit c8e5b9bc8a95d6102cdfb9e0b32f2ebc577db77d[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 12:08:01 2023 +0700

    additional o

[33mcommit a3051c1f0a77f784c327cc1a4d817d3386135c36[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 12:05:14 2023 +0700

    adding pytz to requirements

[33mcommit 2148cdfed64df6db2d02359c1880ff1dab1b5968[m
Author: Matthew McDonnell <mcdonnell.matthew@ymail.com>
Date:   Wed Sep 13 11:59:21 2023 +0700

    Initial upload of CS50 finance

[33mcommit 09edbff796fe2439688dbab20f5e8609edd48970[m
Author: TheBuleGanteng <71803511+TheBuleGanteng@users.noreply.github.com>
Date:   Wed Sep 13 18:09:15 2023 +0700

    Initial commit
