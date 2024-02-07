// Global CSRF Token Variable
let csrfToken = ''; 
let csrfTokenInput = document.querySelector('input[name="csrf_token"]');
if (csrfTokenInput) {
    csrfToken = csrfTokenInput.value;
    console.log("CSRF Token set:", csrfToken);
} else {
    console.log("CSRF token input not found.");
}


window.addEventListener('load', function() {
    var spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.remove('d-flex');
        spinner.style.display = 'none';
    } else {
        console.log("Spinner element not found.");
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded in myFinance50.js.');
    console.log('this is a console.log from myFinance50.js....myFinance50.js loaded successfully');
    
    
    // Declaration of global variables and functions------------------------------------------------------------
    // buy
    window.jsSymbolValidation = jsSymbolValidation
    window.jsSharesValidation = jsSharesValidation
    // password_change
    // password_reset_request
    // password_reset_request_new
    // profile
    window.jsShowHiddenNameField = jsShowHiddenNameField;
    window.jsShowHiddenUsernameField = jsShowHiddenUsernameField; 
    window.jsUpdateTaxRateDisplaySTCG = jsUpdateTaxRateDisplaySTCG;
    window.jsUpdateTaxRateDisplayLTCG = jsUpdateTaxRateDisplayLTCG;
    
    // register
    window.jsPasswordValidation = jsPasswordConfirmationValidation
    window.jsPasswordConfirmationValidation = jsPasswordConfirmationValidation;
    
    // Make the following variables globally accessible 
    let initial_accounting_method;
    let initial_tax_loss_offsets;
    let initial_tax_rate_STCG_value;
    let initial_tax_rate_LTCG_value;
    let debounce_timeout = 200;
    let symbolValidationPassed = false;
    let sharesValidationPassed = false;
    let isButtonClicked = false;

    if (document.getElementById('accounting_method')) {        
        initial_accounting_method = document.getElementById('accounting_method').value;
    }
    if (document.getElementById('tax_loss_offsets')) {        
        initial_tax_loss_offsets = document.getElementById('tax_loss_offsets').value;
    }
    if (document.getElementById('tax_rate_STCG_value')) {
        initial_tax_rate_STCG_value = parseFloat(document.getElementById('tax_rate_STCG_value').innerText.replace('%', ''));
    } 
    if (document.getElementById('tax_rate_LTCG_value')) {
        initial_tax_rate_LTCG_value = parseFloat(document.getElementById('tax_rate_LTCG_value').innerText.replace('%', ''));
    }

    // Allow for tooltip text to appear on any page where it is located. 
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
    });


    // Set debounce function globally
    // Debounce function
    function debounce(func, timeout = debounce_timeout){
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }


    // Determine sequence of JS functions for each page ------------------------------------------------------------
    // javascript for buy ------------------------------------------
    if (window.location.href.includes('/buy')) {
        console.log("Running myFinance50.js for /buy... ");

        var symbol = document.getElementById('symbol');
        var shares = document.getElementById('shares');
        var submitButton = document.getElementById('submit_button');
        

        // Debounced symbol validation function
        function debouncedSymbolValidation() {
            // Immediately disable the submit button when input changes
            submitButton.disabled = true;
            jsSymbolValidation().then(() => {
                jsEnableBuySubmitButton(); // Check if the button should be enabled
            });
        }

        // Function that wraps jsSharesValidation with debouncing
        function debouncedSharesValidation() {
            // Immediately disable the submit button when input changes
            submitButton.disabled = true;
            jsSharesValidation().then(() => {
                jsEnableBuySubmitButton(); // Check if the button should be enabled
            });
        }

        function eventHandler() {
            jsSymbolValidationNew(jsEnableBuySubmitButton); // Validate in real-time
            debounce(debouncedSymbolValidation)(); // Debounce and run additional validation
        }

        if (symbol) {
            symbol.addEventListener('keyup', eventHandler);
            symbol.addEventListener('change', eventHandler);
        }
        
        if (shares) {
            document.getElementById('shares').addEventListener('input', debounce(debouncedSharesValidation, 500)); // Using the same timeout for consistency
        }


        const buyForm = document.querySelector('form[action="/buy"]');
        buyForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent form from submitting
            const confirmModal = new bootstrap.Modal(document.getElementById('confirmBuyModal'));
            confirmModal.show();
        });

        const confirmBuyButton = document.getElementById('confirmBuyButton');
        confirmBuyButton.addEventListener('click', function () {
            buyForm.submit(); // Submit the form
        });

    }
    
    // /javascript for buy ------------------------------------------


    // javascript for password_change ------------------------------------------
    if (window.location.href.includes('/password_change')) {
        console.log("Running myFinance50.js for /password_change... ");

        // Pulls in elements if they exist on page and assigns them to variables
        var email = document.getElementById('email');
        var password_old = document.getElementById('password_old');
        var password = document.getElementById('password');
        var password_confirmation = document.getElementById('password_confirmation');

        // Lists the functions to run if the given elements are on the page
        if (email) {
            document.getElementById('email').addEventListener('input', function() {
                jsEnablePasswordChangeSubmitButton();
            });
        }

        if (password_old) {
            document.getElementById('password_old').addEventListener('input', function() {
                jsEnablePasswordChangeSubmitButton();
            });
        }

        if (password) {
            document.getElementById('password').addEventListener('input', function() {
                jsPasswordValidation();
                jsEnablePasswordChangeSubmitButton();
            });
        }

        if (password_confirmation) {
            document.getElementById('password_confirmation').addEventListener('input', function() {
                jsPasswordConfirmationValidation();
                jsEnablePasswordChangeSubmitButton();
            });
        }
    }
    // javascript for password_change ----------------------------------------


    // javascript for password_request_reset----------------------------------
    if (window.location.pathname === '/password_reset_request') {
        console.log("Running myFinance50.js for /password_reset_request... ");

        // Pulls in elements if they exist on page and assigns them to variables
        var email = document.getElementById('email')

        // Run functions if given elements are present on the page
        if (email) {
            document.getElementById('email').addEventListener('input', function() {
                jsEnablePasswordResetRequestSubmitButton();
            });
        }
    }
    // /javascript for password_request_reset---------------------------------

    
    // javascript for password_request_reset_new------------------------------
    if (window.location.href.includes('/password_reset_request_new')) {
        console.log("Running myFinance50.js for /password_reset_request_new... ");

        // Pulls in elements if they exist on page and assigns them to variables
        var password = document.getElementById('password')
        var password_confirmation = document.getElementById('password_confirmation')

        // Run functions if given elements are present on the page
        if (password) {
            document.getElementById('password').addEventListener('input', function() {
                jsPasswordValidation();
                jsEnablePasswordResetRequestNewSubmitButton();
            });
        }

        if (password_confirmation) {
            document.getElementById('password_confirmation').addEventListener('input', function() {
                jsPasswordConfirmationValidation();
                jsEnablePasswordResetRequestNewSubmitButton();
            });
        }
    }
    // /javascript for password_request_reset_new-----------------------------

        
    // javascript for profile ------------------------------------------------
    if (window.location.href.includes('/profile')) {
        console.log("Running myFinance50.js for /profile... ");
        
        // Pulls in elements if they exist on page and assigns them to variables
        var updateButtonNameFull = document.getElementById('updateButtonNameFull');
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var updateButtonUsername = document.getElementById('updateButtonUsername');
        var username = document.getElementById('username');
        var accounting_method = document.getElementById('accounting_method');
        var tax_loss_offsets = document.getElementById('tax_loss_offsets');
        var tax_rate_STCG= document.getElementById('tax_rate_STCG');
        var tax_rate_STCG_value = document.getElementById('tax_rate_STCG_value');
        var tax_rate_LTCG= document.getElementById('tax_rate_LTCG');
        var tax_rate_LTCG_value = document.getElementById("tax_rate_LTCG_value");
        var profileForm = document.querySelector('form'); // Selects the only form on the page

        // Capture the profile form submission
        if (profileForm) {
            profileForm.addEventListener('submit', function(event) {
                var taxRateSTCGValue = parseFloat(document.getElementById('tax_rate_STCG_value').innerText.replace('%', '')).toFixed(2);
                var hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'tax_rate_STCG'; // The name must match what you expect on the server side
                hiddenInput.value = taxRateSTCGValue;
                profileForm.appendChild(hiddenInput);
            });
        }

        if (updateButtonNameFull) {
            updateButtonNameFull.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent the default anchor action
                jsShowHiddenNameField(); // Call the function
            });
        }

        if (name_first) {
            document.getElementById('name_first').addEventListener('input', function() {
                jsEnableProfileSubmitButton();
            });
        }

        if (name_last) {
            document.getElementById('name_last').addEventListener('input', function() {
                jsEnableProfileSubmitButton();
            });
        }

        if (updateButtonUsername) {
            updateButtonUsername.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent the default anchor action
                jsShowHiddenUsernameField(); // Call the function
            });
        }

        if (username) {
            document.getElementById('username').addEventListener('input', function() {
                jsUsernameValidation(); 
                jsEnableProfileSubmitButton();
            });
        }

            if (accounting_method) {
                document.getElementById('accounting_method').addEventListener('input', function() { 
                    jsEnableProfileSubmitButton();
                });
            }

            if (tax_loss_offsets) {
                document.getElementById('tax_loss_offsets').addEventListener('input', function() { 
                    jsEnableProfileSubmitButton();
                });
            }

        if (tax_rate_STCG) {
            jsUpdateTaxRateDisplaySTCG(tax_rate_STCG, tax_rate_STCG_value);
            tax_rate_STCG.addEventListener('input', function() {
                jsUpdateTaxRateDisplaySTCG(tax_rate_STCG, tax_rate_STCG_value);
                jsEnableProfileSubmitButton();
            });
        }

        if (tax_rate_LTCG) {
            jsUpdateTaxRateDisplayLTCG(tax_rate_STCG, tax_rate_STCG_value);
            document.getElementById('tax_rate_LTCG').addEventListener('input', function() { 
                jsUpdateTaxRateDisplayLTCG(tax_rate_LTCG, tax_rate_LTCG_value);
                jsEnableProfileSubmitButton();
            });
        }

        const buyForm = document.querySelector('form[action="/buy"]');
        buyForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent form from submitting
            const confirmModal = new bootstrap.Modal(document.getElementById('confirmBuyModal'));
            confirmModal.show();
        });

        const confirmBuyButton = document.getElementById('confirmBuyButton');
        confirmBuyButton.addEventListener('click', function () {
            buyForm.submit(); // Submit the form
        });
    }
    // /javascript for profile -----------------------------------------------


    // javascript for quote ---------------------------------------------------
    if (window.location.href.includes('/quote')) {
        console.log("Running myFinance50.js for /quote... ");
        
        var symbol = document.getElementById('symbol');
        var submitButton = document.getElementById('submit_button');
        

        // Debounced symbol validation function
        function debouncedSymbolValidation() {
            // Immediately disable the submit button when input changes
            submitButton.disabled = true;
            jsSymbolValidation().then(() => {
                jsEnableQuoteSubmitButton(); // Check if the button should be enabled
            });
        }

        function eventHandler() {
            jsSymbolValidationNew(jsEnableQuoteSubmitButton); // Validate in real-time
            debounce(debouncedSymbolValidation)(); // Debounce and run additional validation
        }

        if (symbol) {
            symbol.addEventListener('keyup', eventHandler);
            symbol.addEventListener('change', eventHandler);
        }
    }
    // /javascript for quote ---------------------------------------------------


    // javascript for register -----------------------------------------------
    if (window.location.href.includes('/register')) {
        console.log("Running myFinance50.js for /register... ");
        
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var username = document.getElementById('username');
        var email = document.getElementById('email');
        var password = document.getElementById('password');
        var password_confirmation = document.getElementById('password_confirmation');
        var accounting_method = document.getElementById('accounting_method');
        var tax_loss_offsets = document.getElementById('tax_loss_offsets');
        var tax_rate_STCG= document.getElementById('tax_rate_STCG');
        var tax_rate_STCG_value = document.getElementById('tax_rate_STCG_value');
        var tax_rate_LTCG= document.getElementById('tax_rate_LTCG');
        var tax_rate_LTCG_value = document.getElementById("tax_rate_LTCG_value");
        var registerForm = document.querySelector('form'); // Selects the only form on the page

        if (registerForm) {
            registerForm.addEventListener('submit', function(event) {
                var taxRateSTCGValue = parseFloat(document.getElementById('tax_rate_STCG_value').innerText.replace('%', '')).toFixed(2);
                var hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'tax_rate_STCG'; // The name must match what you expect on the server side
                hiddenInput.value = taxRateSTCGValue;
                registerForm.appendChild(hiddenInput);
            });
        }

        if (name_first) {
            document.getElementById('name_first').addEventListener('input', function() {
                jsEnableRegisterSubmitButton();
            });
        }
        
        if (name_last) {
            document.getElementById('name_last').addEventListener('input', function() {
                jsEnableRegisterSubmitButton();
            });
        }
        
        if (email) {
            document.getElementById('email').addEventListener('input', function() {
                jsEmailValidation(); 
                jsEnableRegisterSubmitButton();
            });
        }

        if (username) {
            document.getElementById('username').addEventListener('input', function() {
                jsUsernameValidation(); 
                jsEnableRegisterSubmitButton();
            });
        }

        if (password) {
            document.getElementById('password').addEventListener('input', function() {
                jsPasswordValidation();
                jsEnableRegisterSubmitButton();
            });
        }

        if (password_confirmation) {
            document.getElementById('password_confirmation').addEventListener('input', function() {
                jsPasswordConfirmationValidation();
                jsEnableRegisterSubmitButton();
            });
        }
        if (tax_rate_STCG) {
            jsUpdateTaxRateDisplaySTCG(tax_rate_STCG, tax_rate_STCG_value);
            tax_rate_STCG.addEventListener('input', function() {
                jsUpdateTaxRateDisplaySTCG(tax_rate_STCG, tax_rate_STCG_value);
            });
        }

        if (tax_rate_LTCG) {
            jsUpdateTaxRateDisplayLTCG(tax_rate_STCG, tax_rate_STCG_value);
            document.getElementById('tax_rate_LTCG').addEventListener('input', function() { 
                jsUpdateTaxRateDisplayLTCG(tax_rate_LTCG, tax_rate_LTCG_value);
            });
        }
    } 
    // /javascript for register ----------------------------------------------


    // javascript for sell ------------------------------------------
    if (window.location.href.includes('/sell')) {
        console.log('running myFinance50.js for /sell ... ');
        
        var symbol = document.getElementById('symbol');
        var shares = document.getElementById('shares');
        

        // Function that wraps jsSymbolValidation with debouncing
        function debouncedSharesValidation() {
            jsSharesValidation().then(submit_enabled => {
                jsEnableSellSubmitButton();
            });
        }

        if (symbol) {
            document.getElementById('symbol').addEventListener('input', function() {
                // Trigger jsSharesValidation and jsEnableSellSubmitButton
                jsSharesValidation().then(() => {
                    jsEnableSellSubmitButton();
                });
            });
        }
        
        if (shares) {
            document.getElementById('shares').addEventListener('input', debounce(debouncedSharesValidation, 500)); // Using the same timeout for consistency
        }

        const sellForm = document.querySelector('form[action="/sell"]');
        sellForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent form from submitting
            const confirmModal = new bootstrap.Modal(document.getElementById('confirmSellModal'));
            confirmModal.show();
        });

        const confirmSellButton = document.getElementById('confirmSellButton');
        confirmSellButton.addEventListener('click', function () {
            sellForm.submit(); // Submit the form
        });
    }
    // /javascript for sell ------------------------------------------



    // Function definitions -------------------------------------------------------------------    

    // Function description: Provides real-time feedback to user re availability of username.
    function jsEmailValidation() {
        return new Promise((resolve, reject) => {
            var email = document.getElementById('email').value.trim();
            var email_validation = document.getElementById('email_validation');
            console.log(`Running jsUsernameValidation()`);
            console.log(`Running jsUsernameValidation()... email is: ${email}`);
            console.log(`running jsUsernameValidation()... CSRF Token is: ${csrfToken}`); 

            if (email === '') {
                console.log(`Running jsUsernameValidation()... email ==='' (email is empty)`);
                email_validation.innerHTML = '';
                email_validation.style.display = 'none';
                submit_enabled = false;
                resolve(submit_enabled);
            } else {
                console.log(`Running jsUsernameValidation()... email != '' (email is not empty)`);
                fetch('/check_email_registered', {
                    method: 'POST',
                    body: new URLSearchParams({ 'user_input': email }),
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    }
                })
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    } else {
                        throw new Error('Server responded with a non-200 status');
                    }
                })
                .then(text => {
                    if (text === 'True') {
                        email_validation.innerHTML = 'Email unavailable';
                        email_validation.style.color = 'red';
                        submit_enabled = false;
                    } else {
                        email_validation.innerHTML = 'Email available';
                        email_validation.style.color = '#22bd39';
                        submit_enabled = true;
                    }
                    email_validation.style.display = 'block';
                    resolve(submit_enabled);
                })
                .catch(error => {
                    console.error('Error:', error);
                    email_validation.innerHTML = 'An error occurred. Please try again.';
                    email_validation.style.color = 'red';
                    email_validation.style.display = 'block';
                });
            }
        });
    }


    // Function description: Provides real-time feedback to user whether input meets PW requirements.
    function jsPasswordValidation() {
        return new Promise((resolve, reject) => {
            var password = document.getElementById('password').value.trim();
            var password_confirmation = document.getElementById('password_confirmation').value.trim();
            var regLiMinTotChars = document.getElementById('pw_min_tot_chars_li');
            var regLiMinLetters = document.getElementById('pw_min_letters_li');
            var regLiMinNum = document.getElementById('pw_min_num_li');
            var regLiMinSym = document.getElementById('pw_min_sym_li');
            console.log(`Running jsPasswordValidation()`)
            console.log(`running jsPasswordValidation()... CSRF Token is: ${csrfToken}`);
            
            // Helper function: resets color of element to black
            function resetColor(elements) {
                if (!Array.isArray(elements)) {
                    elements = [elements]; // Wrap the single element in an array
                }
                elements.forEach(element => {
                    element.style.color = 'black';
                });
            }

            // Helper function: set color of element to #22bd39 (success green)
            function setColor(elements) {
                if (!Array.isArray(elements)) {
                    elements = [elements]; // Wrap the single element in an array
                }
                elements.forEach(element => {
                    element.style.color = '#22bd39';
                });
            }
            
            // If password is blank, reset the color of the elements below and return false.
            if (password === '') {
                resetColor([regLiMinTotChars, regLiMinLetters, regLiMinNum, regLiMinSym]);
                return resolve(false);
            }
            // If password is not blank, then toss the value over to the /check_password_strength in app.py
            fetch('/check_valid_password', {
                method: 'POST',
                body: new URLSearchParams({ 
                    'password': password,
                    'password_confirmation': password_confirmation
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                }
            })
            // Do the following with the result received back from app.py
            .then(response => response.json())
            .then(data => {
                let submit_enabled = true;
                if (data.checks_passed.includes('pw_reg_length')) {
                    setColor(regLiMinTotChars);
                } else {
                    resetColor(regLiMinTotChars);
                    submit_enabled = false;
                }
                if (data.checks_passed.includes('pw_req_letter')) {
                    setColor(regLiMinLetters);
                } else {
                    resetColor(regLiMinLetters);
                    submit_enabled = false;
                }
                if (data.checks_passed.includes('pw_req_num')) {
                    setColor(regLiMinNum);
                } else {
                    resetColor(regLiMinNum);
                    submit_enabled = false;
                }
                if (data.checks_passed.includes('pw_req_symbol')) {
                    setColor(regLiMinSym);
                } else {
                    resetColor(regLiMinSym);
                    submit_enabled = false;
                }

                resolve(submit_enabled);
            })
            .catch(error => {
                console.error('Error: password checking in registration has hit an error.', error);
                reject(error);
            });
        });
    }


    // Function description: Provides real-time feedback to user if password == password_confirmation.
    function jsPasswordConfirmationValidation() {
        return new Promise((resolve, reject) => {
            var password = document.getElementById('password').value.trim();
            var password_confirmation = document.getElementById('password_confirmation').value.trim();
            var password_confirmation_validation_match = document.getElementById('password_confirmation_validation_match') 
            console.log(`Running jsPasswordConfirmationValidation()`)
            console.log(`running jsPasswordConfirmationValidation()... CSRF Token is: ${csrfToken}`);
            
            // Helper function: resets color of element to black
            function resetColor(elements) {
                if (!Array.isArray(elements)) {
                    elements = [elements]; // Wrap the single element in an array
                }
                elements.forEach(element => {
                    element.style.color = 'black';
                });
            }

            // Helper function: set color of element to #22bd39 (success green)
            function setColor(elements) {
                if (!Array.isArray(elements)) {
                    elements = [elements]; // Wrap the single element in an array
                }
                elements.forEach(element => {
                    element.style.color = '#22bd39';
                });
            }
            
            // If password is blank, reset the color of the elements below and return false.
            if (password_confirmation === '') {
                resetColor([password_confirmation_validation_match]);
                return resolve(false);
            }
            // If password is not blank, then toss the value over to the /check_password_strength in app.py
            fetch('/check_valid_password', {
                method: 'POST',
                body: new URLSearchParams({ 
                    'password': password,
                    'password_confirmation': password_confirmation
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                }
            })
            // Do the following with the result received back from app.py
            .then(response => response.json())
            .then(data => {
                let submit_enabled = true;
                if (data.confirmation_match == true) {
                    setColor(password_confirmation_validation_match);
                } else {
                    resetColor(password_confirmation_validation_match);
                    submit_enabled = false;
                }
                resolve(submit_enabled);
            })
            .catch(error => {
                console.error('Error: password checking in registration has hit an error.', error);
                reject(error);
            });
        });
    }


    // Function description: Tells user if (a) stock symbol is valid and (b) if the buy or sell txn can proceed.
    function jsSharesValidation() {
        return new Promise((resolve, reject) => {
            var transaction_type = document.getElementById('transaction_type').value;
            var symbol = document.getElementById('symbol').value.trim();
            var shares = document.getElementById('shares').value;
            var shares_validation = document.getElementById('shares_validation');
            console.log(`Running jsSharesValidation()`);
            console.log(`Running jsSharesValidation()... symbol is: ${symbol}`);
            console.log(`running jsSharesValidation()... CSRF Token is: ${csrfToken}`);
            
            sharesValidationPassed = false;

            if (shares === '' || symbol === '') {
                console.log(`Running jsSharesValidation()... shares or symbol is empty)`);
                shares_validation.innerHTML = '';
                shares_validation.style.display = 'none';
                sharesValidationPassed = false;
                resolve(sharesValidationPassed);
            } else {
                console.log(`Running jsSharesValidation()... shares is not empty`);
                fetch('/check_valid_shares', {
                    method: 'POST',
                    body: new URLSearchParams({ 'user_input_symbol': symbol, 'user_input_shares': shares, 'transaction_type': transaction_type }),
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    }
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Running jsSharesValidation()... server responded with a non-200 status');
                    }
                })
                .then(response => {
                    if (response['status'] === 'error') {
                        shares_validation.innerHTML = response['message'];
                        shares_validation.style.color = 'red';
                        sharesValidationPassed = false;
                    } else {
                        shares_validation.innerHTML = response['message']
                        shares_validation.style.color = '#22bd39';
                        sharesValidationPassed = true;
                    }
                    shares_validation.style.display = 'block';
                    resolve(sharesValidationPassed);
                })
                .catch(error => {
                    console.error('Error:', error);
                    shares_validation.innerHTML = 'An error occurred. Please try again.';
                    shares_validation.style.color = 'red';
                    shares_validation.style.display = 'block';
                    sharesValidationPassed = false;
                    resolve(sharesValidationPassed);
                });
            }
        });
    }


    // Function description: When box is clicked, input boxes for fist and last name appear.
    function jsShowHiddenNameField() {
        var profile_hidden_name_container = document.getElementById('profile_hidden_name_container');
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var updateButtonNameFull = document.getElementById('updateButtonNameFull');
        console.log(`Running jsShowHiddenNameField()`)
        console.log(`Running jsShowHiddenNameField()...`)
        console.log(`Running jsShowHiddenNameField()... CSRF Token is ${csrfToken}`);

        
        /* Check if hidden content is already displayed */
        if (profile_hidden_name_container.style.display === 'block') {
            // Hide the container and clear the input field
            profile_hidden_name_container.style.display = 'none';
            name_first.value = '';
            name_last.value = '';
            updateButtonNameFull.innerHTML = 'update';
            updateButtonNameFull.color = 'grey';
            updateButtonNameFull.classList.remove('btn-secondary');
            updateButtonNameFull.classList.add('btn-primary');
        } else {
            // Show the container
            profile_hidden_name_container.style.display = 'block';
            updateButtonNameFull.innerHTML = 'undo';
            updateButtonNameFull.classList.remove('btn-primary');
            updateButtonNameFull.classList.add('btn-secondary');
        }
    }


    // Function description: When box is clicked, input boxes for username appears.
    function jsShowHiddenUsernameField() {
        /* Pull in the relevant elements from the html */
        var profile_hidden_username_container = document.getElementById('profile_hidden_username_container');
        var username = document.getElementById('username');
        var updateButtonUsername = document.getElementById('updateButtonUsername');
        console.log(`Running jsShowHiddenUsernameField()`)
        console.log(`Running jsShowHiddenUsernameField()...`)
        console.log(`Running jsShowHiddenUsernameField()... CSRF Token is ${csrfToken}`);
        
        /* Check if hidden content is already displayed */
        if (profile_hidden_username_container.style.display === 'block') {
            // Hide the container and clear the input field
            profile_hidden_username_container.style.display = 'none';
            username.value = '';
            updateButtonUsername.innerHTML = 'update';
            updateButtonUsername.color = 'grey';
            updateButtonUsername.classList.remove('btn-secondary');
            updateButtonUsername.classList.add('btn-primary');
        } else {
            // Show the container
            profile_hidden_username_container.style.display = 'block';
            updateButtonUsername.innerHTML = 'undo';
            updateButtonUsername.classList.remove('btn-primary');
            updateButtonUsername.classList.add('btn-secondary');
        }
    }


    // Function description: Tells user if a stock symbol.
    function jsSymbolValidation() {
        return new Promise((resolve, reject) => {
            var symbol = document.getElementById('symbol').value.trim();
            var shares = document.getElementById('shares');
            var symbol_validation = document.getElementById('symbol_validation');
            console.log(`Running jsSymbolValidation()`);
            console.log(`Running jsSymbolValidation()... symbol is: ${symbol}`);
            console.log(`running jsSymbolValidation()... CSRF Token is: ${csrfToken}`);

            symbolValidationPassed = false;

            if (symbol === '') {
                console.log(`Running jsSymbolValidation()... symbol ===' ' (symbol is empty)`);
                symbol_validation.innerHTML = '';
                symbol_validation.style.display = 'none';
                symbolValidationPassed = false;
                resolve(symbolValidationPassed);
            } else {
                console.log(`Running jsSymbolValidation()... symbol is not empty. Symbol is: ${ symbol }`);
                fetch('/check_valid_symbol', {
                    method: 'POST',
                    body: new URLSearchParams({ 'user_input': symbol }),
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    }
                })
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    } else {
                        throw new Error('Running jsSymbolValidation()... server responded with a non-200 status');
                    }
                })
                .then(text => {
                    if (text === 'False') {
                        symbol_validation.innerHTML = 'Invalid symbol';
                        symbol_validation.style.color = 'red';
                        symbolValidationPassed = false;
                    } else {
                        symbol_validation.innerHTML = 'Valid symbol';
                        symbol_validation.style.color = '#22bd39';
                        symbolValidationPassed = true;
                    }
                    symbol_validation.style.display = 'block';
                    resolve(symbolValidationPassed);
                })
                .catch(error => {
                    console.error('Error:', error);
                    symbol_validation.innerHTML = 'An error occurred. Please try again.';
                    symbol_validation.style.color = 'red';
                    symbol_validation.style.display = 'block';
                    sharesValidationPassed = false;
                    resolve(sharesValidationPassed);
                });
            }
        });
    }


    // Function description: Validates user input, searching on symbol or company name
    function jsSymbolValidationNew(enableSubmitButtonFunction) {
        var symbol = document.getElementById('symbol');
        var symbol_validation2 = document.getElementById('symbol_validation2');
        console.log(`Running jsSymbolValidationNew()`);
        console.log(`Running jsSymbolValidationNew()... symbol is: ${symbol}`);
        console.log(`running jsSymbolValidationNew()... CSRF Token is: ${csrfToken}`);
    
        // Handles if no user entry for symbol
        if (symbol.value.trim() === '') {
            console.log(`Running jsSymbolValidationNew()... symbol ===' ' (symbol is empty)`);
            symbol_validation2.innerHTML = '';
            symbol_validation2.style.display = 'none';
            
        // Handles if there is user entry for symbol
        } else {
                console.log(`Running jsSymbolValidationNew()... symbol is not empty. Symbol is: ${ symbol }`);
                fetch('/check_valid_symbol_new', {
                method: 'POST',
                body: new URLSearchParams({ 'user_input': symbol.value.trim() }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                }
            })
            // Take the response from check_valid_symbol_new() and parse it
            .then(response => response.json()) 
            .then(data => {
                // First, clear any existing contents from symbol_validation2 and make the object visible
                symbol_validation2.innerHTML = '';
                symbol_validation2.style.display = 'block';
                // Iterate over the data and append each result to symbol_validation2's innerHTML
                data.forEach(item => {
                    // Create a new child div for each record in the JSON object
                    const div = document.createElement('div')
                    // Populate that newly-created div as follows.
                    div.innerHTML = `${item.symbol} - ${item.name} - ${item.exchange_short}<br/>`;
                    // Add the 'result-button' class to this div
                    div.classList.add('btn', 'btn-outline-secondary', 'custom-btn-company-search');
                    // Set click event listener for each button
                    div.addEventListener('click', function() {
                        symbol.blur(); // Remove focus from the input
                        symbol.value = item.symbol; // Populate the symbol input field with the clicked symbol
                        jsSymbolValidation().then(() => { // Validate the newly populated symbol
                            if (enableSubmitButtonFunction && typeof enableSubmitButtonFunction === 'function') {
                                enableSubmitButtonFunction(); // Call the passed function to enable the submit button
                            }
                        });
                    });
                    // Append the new child div to the parent container
                    symbol_validation2.appendChild(div);
                });

                if (data.length === 0) {
                    // If no results, display a message
                    symbol_validation2.innerHTML = '';
                    symbol_validation2.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                symbol_validation2.innerHTML = 'Error fetching symbol data';
            });
        }
    }    


    // Function description: Enables and shows submit button provided the user has
    function jsUpdateTaxRateDisplaySTCG(slider, display) {
        var hiddenInput = document.getElementById('tax_rate_STCG_hidden');
        var newTaxRate = parseFloat(slider.value).toFixed(2);
        display.innerHTML = newTaxRate + '%';
        // Update the hidden field
        if (hiddenInput) {
            hiddenInput.value = newTaxRate;
        }
    }

    
    // Function description: Enables and shows submit button provided the user has
    function jsUpdateTaxRateDisplayLTCG(slider, display) {
        var hiddenInput = document.getElementById('tax_rate_LTCG_hidden');
        var newTaxRate = parseFloat(slider.value).toFixed(2);
        display.innerHTML = newTaxRate + '%';
        // Update the hidden field
        if (hiddenInput) {
            hiddenInput.value = newTaxRate;
        }
    }


    // Function description: Real-time feedback re availability of username.
    function jsUsernameValidation() {
        return new Promise((resolve, reject) => {
            var username = document.getElementById('username').value.trim();
            var username_validation = document.getElementById('username_validation');
            console.log(`Running jsUsernameValidation()`);
            console.log(`Running jsUsernameValidation()... username is: ${username}`);
            console.log(`running jsUsernameValidation()... CSRF Token is: ${csrfToken}`); 

            if (username === '') {
                console.log(`Running jsUsernameValidation()... username ==='' (username is empty)`);
                username_validation.innerHTML = '';
                username_validation.style.display = 'none';
                submit_enabled = false;
                resolve(submit_enabled);
            } else {
                console.log(`Running jsUsernameValidation()... username != '' (username is not empty)`);
                fetch('/check_username_registered', {
                    method: 'POST',
                    body: new URLSearchParams({ 'user_input': username }),
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    }
                })
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    } else {
                        throw new Error('Server responded with a non-200 status');
                    }
                })
                .then(text => {
                    if (text === 'True') {
                        username_validation.innerHTML = 'Username unavailable';
                        username_validation.style.color = 'red';
                        submit_enabled = false;
                    } else {
                        username_validation.innerHTML = 'Username available';
                        username_validation.style.color = '#22bd39';
                        submit_enabled = true;
                    }
                    username_validation.style.display = 'block';
                    resolve(submit_enabled);
                })
                .catch(error => {
                    console.error('Error:', error);
                    username_validation.innerHTML = 'An error occurred. Please try again.';
                    username_validation.style.color = 'red';
                    username_validation.style.display = 'block';
                });
            }
        });
    }

    // Function description: Enables buy button at /buy   
    function jsEnableBuySubmitButton() {
        var submitButton = document.getElementById('submit_button');
        
        // Initially disable submit to ensure button is disabled while promises are in progress
        console.log(`Running jsEnableBuySubmitButton()`)
        console.log(`Running jsEnableBuySubmitButton()... CSRF Token is: ${csrfToken}`);

        // Initially disable submit to prevent premature submissions
        submitButton.disabled = true;

        if (symbolValidationPassed && sharesValidationPassed) {
            console.log('Enabling submit button.');
            submitButton.disabled = false;
        } else {
            console.log('Disabling submit button due to failed or incomplete validation.');
            submitButton.disabled = true;
        }
    }

    
    // Function description: Enables and shows submit button provided the user has
    // updated all of the input fields and that input is.
    function jsEnablePasswordResetRequestSubmitButton() {
        var email = document.getElementById('email').value.trim();
        var submitButton = document.getElementById('submit_button');

        console.log(`Running jsEnablePasswordResetRequestSubmitButton()`)
        console.log(`Running jsEnablePasswordResetRequestSubmitButton()... CSRF Token is: ${csrfToken}`);
        
        if (email === "" ) {
            submitButton.disabled = true;
            console.log(`Running jsEnablePasswordResetRequestSubmitButton()... Submit button disabled.`);
        } else {
            // All validations passed
            console.log(`Running jsEnablePasswordResetRequestSubmitButton()... All validation checks passed, enabling submit button.`);
            submitButton.disabled = false;
        }
    }


    // Function description: Enables and shows submit button provided the user has
    // updated all of the input fields and that input is.
    async function jsEnablePasswordResetRequestNewSubmitButton() {
        var password = document.getElementById('password').value.trim();
        var password_confirmation = document.getElementById('password_confirmation').value.trim();
        var submitButton = document.getElementById('submit_button');

        // Initially disable submit to ensure button is disabled while promises are in progress
        submitButton.disabled = true;

        // Create an array of promises with labels
        var labeledPromises = [
            { label: 'Password Check', promise: jsPasswordValidation() },
            { label: 'Password Confirmation Check', promise: jsPasswordConfirmationValidation() }
        ];
        console.log(`Running jsEnablePasswordResetRequestNewSubmitButton()`)
        console.log(`Running jsEnablePasswordResetRequestNewSubmitButton()... CSRF Token is: ${csrfToken}`);

        Promise.all(labeledPromises.map(labeledPromise => {
            // Add a console.log statement before each promise
            //console.log(`Running jsEnablePasswordResetRequestNewSubmitButton()... Executing promise: ${labeledPromise.label}`);
    
            return labeledPromise.promise.then(result => {
                // Add a console.log statement after each promise resolves
                console.log(`Running jsEnablePasswordResetRequestNewSubmitButton()... Promise (${labeledPromise.label}) resolved with result: ${result}`);
                return { label: labeledPromise.label, result: result };
            });
        }))
            .then((results) => {
                // Log each promise result
                results.forEach(res => {
                    console.log(`Result of ${res.label}: ${res.result}`);
                });
    
                // Check if any of the promises return false
                var allPromisesPassed = results.every(res => res.result === true);
                
                if (!allPromisesPassed) {
                    submitButton.disabled = true;
                    console.log(`Running jsEnablePasswordResetRequestNewSubmitButton()... Submit button disabled.`);
                } else {
                    // All validations passed
                    console.log(`Running jsEnablePasswordResetRequestNewSubmitButton()... All validation checks passed, enabling submit button.`);
                    submitButton.disabled = false;
                }
            }).catch((error) => {
                // Handle errors if any of the Promises reject
                console.error(`Running jsEnablePasswordResetRequestNewSubmitButton()... Error is: ${error}.`);
                submitButton.disabled = true;
            });
    }


    // Function description: Enables and shows submit button provided the user has
    // updated all of the input fields and that input is.
    async function jsEnablePasswordChangeSubmitButton() {
        var email = document.getElementById('email').value.trim();
        var password_old = document.getElementById('password_old').value.trim();
        var submitButton = document.getElementById('submit_button');

        // Initially disable submit to ensure button is disabled while promises are in progress
        submitButton.disabled = true;

        // Create an array of promises with labels
        var labeledPromises = [
            { label: 'Password Check', promise: jsPasswordValidation() },
            { label: 'Password Confirmation Check', promise: jsPasswordConfirmationValidation() }
        ];
        console.log(`Running jsEnablePasswordChangeSubmitButton()`)
        console.log(`Running jsEnablePasswordChangeSubmitButton()... CSRF Token is: ${csrfToken}`);

        Promise.all(labeledPromises.map(labeledPromise => {
            // Add a console.log statement before each promise
            //console.log(`Running jsEnablePasswordChangeSubmitButton()... Executing promise: ${labeledPromise.label}`);
    
            return labeledPromise.promise.then(result => {
                // Add a console.log statement after each promise resolves
                console.log(`Running jsEnablePasswordChangeSubmitButton()... Promise (${labeledPromise.label}) resolved with result: ${result}`);
                return { label: labeledPromise.label, result: result };
            });
        }))
            .then((results) => {
                // Log each promise result
                results.forEach(res => {
                    console.log(`Result of ${res.label}: ${res.result}`);
                });
    
                // Check if any of the promises return false
                var allPromisesPassed = results.every(res => res.result === true);
                
                if (!allPromisesPassed || email === '' || password_old === "" ) {
                    submitButton.disabled = true;
                    console.log(`Running jsEnablePasswordChangeSubmitButton()... Submit button disabled.`);
                } else {
                    // All validations passed
                    console.log(`Running jsEnablePasswordChangeSubmitButton()... All validation checks passed, enabling submit button.`);
                    submitButton.disabled = false;
                }
            }).catch((error) => {
                // Handle errors if any of the Promises reject
                console.error(`Running jsEnablePasswordChangeSubmitButton()... Error is: ${error}.`);
                submitButton.disabled = true;
            });
    }


    // Function description: Enables and shows submit button provided the user has
    // updated any of the input fields.
    async function jsEnableProfileSubmitButton() {
        var name_first = document.getElementById('name_first').value.trim();
        var name_last = document.getElementById('name_last').value.trim();
        var username = document.getElementById('username').value.trim();
        var username_validation = document.getElementById('username_validation');
        var updated_accounting_method = document.getElementById('accounting_method').value;
        var updated_tax_loss_offsets = document.getElementById('tax_loss_offsets').value;
        var updated_tax_rate_STCG_value = parseFloat(document.getElementById('tax_rate_STCG_value').innerText.replace('%', ''));
        var updated_tax_rate_LTCG_value = parseFloat(document.getElementById('tax_rate_LTCG_value').innerText.replace('%', ''));
                
        if (username !== '') {
            await jsUsernameValidation();
        }

        var username_validation = username_validation.innerText || username_validation.textContent;
        var submitButton = document.getElementById('submit_button');
        console.log(`Running jsEnableProfileSubmitButton()...`)
        console.log(`Running jsEnableProfileSubmitButton()... value for username_validation is: ${ username_validation}`)
        console.log(`Running jsEnableProfileSubmitButton()... CSRF Token is ${csrfToken}`);


        console.log("Input Values:", {
            name_first,
            name_last,
            username,
            username_validation,
            updated_accounting_method,
            updated_tax_loss_offsets,
            updated_tax_rate_STCG_value,
            updated_tax_rate_LTCG_value,
        });

        // Logic: If any user input field != empty && username_validation passes, enable submit button
        if (
            (name_first !== '' || name_last !== '' || username !== '' || updated_accounting_method !== initial_accounting_method || updated_tax_loss_offsets !== initial_tax_loss_offsets || updated_tax_rate_STCG_value !== initial_tax_rate_STCG_value || updated_tax_rate_LTCG_value !== initial_tax_rate_LTCG_value || updated_tax_loss_offsets !== initial_tax_loss_offsets) &&
            username_validation !== 'Username unavailable'
        ) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    }


    // Function description: Enables buy button at /quote
    function jsEnableQuoteSubmitButton() {
        var submitButton = document.getElementById('submit_button');
        
        // Initially disable submit to ensure button is disabled while promises are in progress
        console.log(`Running jsEnableQuoteSubmitButton() ... `)
        console.log(`Running jsEnableQuoteSubmitButton() ... CSRF Token is: ${csrfToken}`);

        // Initially disable submit to prevent premature submissions
        submitButton.disabled = true;

        if (symbolValidationPassed) {
            console.log('Running jsEnableQuoteSubmitButton() ... enabling submit button.');
            submitButton.disabled = false;
        } else {
            console.log('Running jsEnableQuoteSubmitButton() ... disabling submit button due to failed or incomplete validation.');
            submitButton.disabled = true;
        }
    }


    // Function description: Enables and shows submit button provided the user has
    // updated all of the input fields and that input is.
    async function jsEnableRegisterSubmitButton() {
        var name_first = document.getElementById('name_first').value.trim();
        var name_last = document.getElementById('name_last').value.trim();
        var submitButton = document.getElementById('submit_button');

        // Initially disable submit to ensure button is disabled while promises are in progress
        submitButton.disabled = true;

        // Create an array of promises with labels
        var labeledPromises = [
            { label: 'Username Validation', promise: jsUsernameValidation() },
            { label: 'Email Validation', promise: jsEmailValidation() },
            { label: 'Password Check', promise: jsPasswordValidation() },
            { label: 'Password Confirmation Check', promise: jsPasswordConfirmationValidation() }
        ];
        console.log(`Running jsEnableRegisterSubmitButton()`)
        console.log(`Running jsEnableRegisterSubmitButton()... CSRF Token is: ${csrfToken}`);

        Promise.all(labeledPromises.map(labeledPromise => {
            // Add a console.log statement before each promise
            console.log(`Running jsEnableRegisterSubmitButton()... Executing promise: ${labeledPromise.label}`);
    
            return labeledPromise.promise.then(result => {
                // Add a console.log statement after each promise resolves
                console.log(`Running jsEnableRegisterSubmitButton()... Promise (${labeledPromise.label}) resolved with result: ${result}`);
                return { label: labeledPromise.label, result: result };
            });
        }))
            .then((results) => {
                // Log each promise result
                results.forEach(res => {
                    console.log(`Result of ${res.label}: ${res.result}`);
                });
    
                // Check if any of the promises return false
                var allPromisesPassed = results.every(res => res.result === true);
                
                if (!allPromisesPassed || name_first === '' || name_last === "" ) {
                    submitButton.disabled = true;
                    console.log(`Running jsEnableRegisterSubmitButton()... Submit button disabled.`);
                } else {
                    // All validations passed
                    console.log(`Running jsEnableRegisterSubmitButton()... All validation checks passed, enabling submit button.`);
                    submitButton.disabled = false;
                }
            }).catch((error) => {
                // Handle errors if any of the Promises reject
                console.error(`Running jsEnableRegisterSubmitButton()... Error is: ${error}.`);
                submitButton.disabled = true;
            });
    }


    // Function description: Enables buy button at /sell
    function jsEnableSellSubmitButton() {
        var symbol = document.getElementById('symbol').value.trim();
        var submitButton = document.getElementById('submit_button');
        console.log(`running jsEnableSellSubmitButton ... sharesValidationPassed is: ${sharesValidationPassed}`);
        console.log(`running jsEnableSellSubmitButton ... symbol is: ${symbol}`);

        // Initially disable submit to ensure button is disabled while promises are in progress
        submitButton.disabled = true;

        if (symbol != '' && sharesValidationPassed) {
            console.log('Enabling submit button.');
            submitButton.disabled = false;
        } else {
            console.log('Disabling submit button due to failed or incomplete validation.');
            submitButton.disabled = true;
        }
    }
    
});