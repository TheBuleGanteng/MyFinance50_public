document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded in savorscript.js.');
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
    // profile
    window.jsShowHiddenInputName = jsShowHiddenInputName;
    window.jsShowHiddenInputUsername = jsShowHiddenInputUsername; 
    window.jsEnableProfileSubmitButton = jsEnableProfileSubmitButton;



    // javascript for /profile --------------------------------------------------------------
    if (window.location.href.includes('/profile')) {
        console.log("Running myFinance50.js for /profile... ");
        
        // Pulls in elements if they exist on page and assigns them to variables
        var updateButtonNameNameFull = document.getElementById('updateButtonNameNameFull');
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var updateButtonNameUsername = document.getElementById('updateButtonNameUsernameOld');
        var username = document.getElementById('username');

        // Lists the functions to run if the given elements are on the page
        if (updateButtonNameNameFull) {
            updateButtonNameNameFull.addEventListener('click', function(event) {
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

        if (updateButtonNameUsername) {
            updateButtonNameUsername.addEventListener('click', function(event) {
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



    // Function description: When box is clicked, input boxes for fist and last name appear.
    function jsShowHiddenNameField() {
        /* Pull in the relevant elements from the html */
        var profile_hidden_name_container = document.getElementById('profile_hidden_name_container');
        var name_first = document.getElementById('name_first');
        var name_last = document.getElementById('name_last');
        var updateButtonName = document.getElementById('updateButtonNameName');
        console.log(`Running jsShowHiddenNameField()`)
        console.log(`Running jsShowHiddenNameField()...`)
        console.log(`Running jsShowHiddenNameField()... CSRF Token is ${csrfToken}`);

        
        /* Check if hidden content is already displayed */
        if (profile_hidden_name_container.style.display === 'block') {
            // Hide the container and clear the input field
            profile_hidden_name_container.style.display = 'none';
            name_first.value = '';
            name_last.value = '';
            updateButtonName.innerHTML = 'update';
            updateButtonName.color = 'grey';
            updateButtonName.classList.remove('btn-secondary');
            updateButtonName.classList.add('btn-primary');
        } else {
            // Show the container
            profile_hidden_name_container.style.display = 'block';
            updateButtonName.innerHTML = 'undo';
            updateButtonName.classList.remove('btn-primary');
            updateButtonName.classList.add('btn-secondary');
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
            console.log(`Running jsUsernameValidation()`)
            console.log(`Running jsUsernameValidation()... username is: ${username}`)
            console.log(`running jsUsernameValidation()... CSRF Token is: ${csrfToken}`); 

            // Username input is empty, hide the validation message and submit button
            if (username === '') {
                console.log(`Running jsUsernameValidation()... username ==='' (username is empty)`)
                username_validation.innerHTML = '';
                username_validation.style.display = 'none';
                submit_enabled = false;
                resolve(submit_enabled);
    
            // If username != empty, do the following...
            } else {
                console.log(`Running jsUsernameValidation()... username != '' (username is not not empty)`)
                fetch('/check_username_registered', {
                    method: 'POST',
                    body: new URLSearchParams({ 'username': username }),
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    }
                })
                .then(response => response.text()) 
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
                    // Handle any errors here
                    console.error('Error:', error);
                    username_validation.innerHTML = 'Username available';
                    username_validation.style.color = '#22bd39';
                    username_validation.style.display = 'block';
                });
            }
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

});