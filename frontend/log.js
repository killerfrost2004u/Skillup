const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

// --- CRITICAL FIX: Wrap logic to ensure all HTML elements are loaded ---
document.addEventListener('DOMContentLoaded', () => {

    // Form elements (now correctly retrieved because the DOM is loaded)
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');

    // API Configuration - Set the base URL for your Flask app
    const API_BASE_URL = 'http://localhost:5000';

    // --- Utility Functions ---

    function displayMessage(message, isSuccess = true) {
        // Using alert for immediate feedback (change this to a modern modal later!)
        console.log(`[${isSuccess ? 'SUCCESS' : 'ERROR'}] ${message}`);
        alert(message);
    }

    // Function to handle Fetch with Exponential Backoff for reliable network requests
    async function fetchWithRetry(url, options, maxRetries = 3) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                const response = await fetch(url, options);

                // If response is OK or a permanent client error (4xx), return it.
                if (response.ok || (response.status >= 400 && response.status < 500)) {
                    return response;
                }

                // Server error (5xx) - will retry
                console.warn(`Attempt ${i + 1} failed with status ${response.status}. Retrying...`);

            } catch (error) {
                // Network error (no connection) - will retry
                console.error(`Network error on attempt ${i + 1}: ${error.message}. Retrying...`);
            }

            // Wait using exponential backoff: 1s, 2s, 4s...
            if (i < maxRetries - 1) {
                const delay = Math.pow(2, i) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        throw new Error("API request failed after multiple retries. Check if server is running.");
    }


    // --- Form Handlers ---

    // Handle Registration Submission
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            // CRITICAL: Stops the browser's default GET form submission
            e.preventDefault();

            const username = document.getElementById('register-username').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;

            try {
                const response = await fetchWithRetry(`${API_BASE_URL}/register`, {
                    method: 'POST', // Correct HTTP method
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, email, password }),
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(result.message || 'Registration successful! Proceeding to login.', true);

                    // Switch to login tab after successful registration
                    container.classList.remove('active');
                    registerForm.reset(); // Clear the form
                } else {
                    displayMessage(result.message || result.error || 'Registration failed.', false);
                }
            } catch (error) {
                displayMessage(`A critical network error occurred: ${error.message}. Is the Flask backend running?`, false);
            }
        });
    }

    // Handle Login Submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            // CRITICAL: Stops the browser's default GET form submission
            e.preventDefault();

            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetchWithRetry(`${API_BASE_URL}/login`, {
                    method: 'POST', // Correct HTTP method
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(`Login successful! Welcome ${result.username}. Redirecting to the dashboard.`, true);

                    // *** NEW REDIRECT ACTION ***
                    // Redirects user to the main page of the application
                    window.location.href = './SKILL UP.html';

                } else {
                    displayMessage(result.message || result.error || 'Login failed. Check username and password.', false);
                }
            } catch (error) {
                displayMessage(`A critical network error occurred: ${error.message}. Is the Flask backend running?`, false);
            }
        });
    }

}); // --- END of DOMContentLoaded listener ---

// --- Existing Toggle Logic (for UI transition) ---

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
})

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
})
