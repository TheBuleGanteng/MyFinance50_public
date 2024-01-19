document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded in myFinance50.js.');
    console.log('this is a console.log from myFinance50.js....myFinance50.js loaded successfully');

    // Global CSRF Token Variable
    let csrfToken = ''; 
    let csrfTokenInput = document.querySelector('input[name="csrf_token"]');
    if (csrfTokenInput) {
        csrfToken = csrfTokenInput.value;
        console.log("CSRF Token set:", csrfToken);
    } else {
        console.log("CSRF token input not found.");
    }

    // Make the functions globally accessible
    // password_change
    // password_reset_request
    window.jsEnablePasswordResetRequestSubmitButton = jsEnablePasswordResetRequestSubmitButton;
    // password_reset_request_new
    window.jsEnablePasswordResetRequestNewSubmitButton = jsEnablePasswordResetRequestNewSubmitButton;
    // profile
    window.jsShowHiddenNameField = jsShowHiddenNameField;
    window.jsShowHiddenUsernameField = jsShowHiddenUsernameField; 
    window.jsEnableProfileSubmitButton = jsEnableProfileSubmitButton;
    // register
    window.jsPasswordValidation = jsPasswordConfirmationValidation
    window.jsPasswordConfirmationValidation = jsPasswordConfirmationValidation;
    window.jsEnableRegisterSubmitButton = jsEnableRegisterSubmitButton;

    
    // javascript for /password_change ------------------------------------------------------
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
    // javascript for /password_change ------------------------------------------------------


    // javascript for /password_request_reset------------------------------------------------
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

    // /javascript for /password_request_reset------------------------------------------------

    
    // javascript for /password_request_reset_new------------------------------------------------
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
    // /javascript for /password_request_reset_new------------------------------------------------

        
    // javascript for /profile --------------------------------------------------------------
    if (window.location.href.includes('/profile')) {
        console.log("Running myFinance50.js for /profile... ");
        
        // Pulls in elements if they exist on page and assigns them to variables
        var updateButtonNameFull = document.getElementById('updateButtonNameFull');
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var updateButtonUsername = document.getElementById('updateButtonUsername');
        var username = document.getElementById('username');

        // Lists the functions to run if the given elements are on the page
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
    }
    // /javascript for /profile --------------------------------------------------------------


    // javascript for /register --------------------------------------------------------------
    if (window.location.href.includes('/register')) {
        console.log("Running myFinance50.js for /register... ");
        
        // Pulls in elements if they exist on page and assigns them to variables
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var username = document.getElementById('username');
        var email = document.getElementById('email');
        var password = document.getElementById('password');
        var password_confirmation = document.getElementById('password_confirmation');


        // Lists the functions to run if the given elements are on the page
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
    } 
    // /javascript for /register --------------------------------------------------------------



    // Function description: When box is clicked, input boxes for fist and last name appear.
    function jsShowHiddenNameField() {
        /* Pull in the relevant elements from the html */
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
        });

        // Logic: If any user input field != empty && username_validation passes, enable submit button
        if (
            (name_first !== '' || name_last !== '' || username !== '' ) &&
            username_validation !== 'Username unavailable'
        ) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    }



    // Function description: Enables and shows submit button provided the user has
    // updated all of the input fields and that input is.
    async function jsEnableRegisterSubmitButton() {
        var name_first = document.getElementById('name_first').value.trim();
        var name_last = document.getElementById('name_last').value.trim();
        var submitButton = document.getElementById('submit_button');

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
    
});