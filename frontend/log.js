document.addEventListener('DOMContentLoaded', () => {
    // --- Auto-show register panel if redirected ---
    const urlParams = new URLSearchParams(window.location.search);
    const showRegister = urlParams.get('show') === 'register';
    
    if (showRegister) {
        const container = document.querySelector('.container');
        if (container) {
            container.classList.add('active');
        }
    }

    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');

    let messageBox = document.createElement('div');
    messageBox.id = 'message-box';
    messageBox.style.position = 'fixed';
    messageBox.style.top = '20px';
    messageBox.style.left = '50%';
    messageBox.style.transform = 'translateX(-50%)';
    messageBox.style.padding = '15px 25px';
    messageBox.style.backgroundColor = 'rgb(51, 142, 205)';
    messageBox.style.color = 'white';
    messageBox.style.fontSize = '16px';
    messageBox.style.borderRadius = '8px';
    messageBox.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
    messageBox.style.zIndex = '1000';
    messageBox.style.display = 'none';
    document.body.appendChild(messageBox);

    function showMessage(msg, duration = 3000) {
        messageBox.textContent = msg;
        messageBox.style.display = 'block';
        setTimeout(() => { messageBox.style.display = 'none'; }, duration);
    }

    // ----------- REGISTER -----------
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const username = document.getElementById("register-username").value;
            const email = document.getElementById("register-email").value;
            const password = document.getElementById("register-password").value;

            try {
                const res = await fetch(`${API_BASE_URL}/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await res.json();

                if(res.ok){
                    showMessage("Registered successfully! Logging you in...");
                    
                    // Auto-login after registration
                    try {
                        const loginRes = await fetch(`${API_BASE_URL}/login`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ username, password })
                        });
                        
                        const loginData = await loginRes.json();
                        
                        if(loginRes.ok && loginData.token) {
                            // Save the JWT token
                            localStorage.setItem("token", loginData.token);
                            
                            // Save user data
                            localStorage.setItem("user", JSON.stringify({
                                user_id: loginData.user_id,
                                name: loginData.name,
                                email: loginData.email,
                                role: loginData.role || 'student',
                                profile_image: loginData.profile_image || "user.jpg",
                                age: loginData.age || 20,
                                year: loginData.year || "Year",
                                major: loginData.major || "Computer",
                                college: loginData.college || "College"
                            }));
                            
                            showMessage("Login successful!");
                            setTimeout(() => { window.location.href = "prof.html"; }, 1000);
                        } else {
                            // If auto-login fails
                            showMessage("Registration complete! Please login.");
                            setTimeout(() => { window.location.href = "log.html"; }, 1500);
                        }
                    } catch(err) {
                        showMessage("Registration complete! Please login.");
                        setTimeout(() => { window.location.href = "log.html"; }, 1500);
                    }
                } else {
                    showMessage(data.message);
                }

            } catch(err) {
                showMessage("Network Error: " + err.message);
            }
        });
    }

    // ----------- LOGIN -----------
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const username = document.getElementById("login-username").value;
            const password = document.getElementById("login-password").value;

            try {
                const res = await fetch(`${API_BASE_URL}/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });

                const data = await res.json();
                
                if(res.ok){
                    // Save the JWT token
                    if (data.token) {
                        localStorage.setItem("token", data.token);
                    }

                    // Save user data
                    localStorage.setItem("user", JSON.stringify({
                        user_id: data.user_id,
                        name: data.name,
                        email: data.email,
                        role: data.role || 'student',
                        profile_image: data.profile_image || "user.jpg",
                        age: data.age || 20,
                        year: data.year || "Year",
                        major: data.major || "Computer",
                        college: data.college || "College"
                    }));
                    
                    showMessage("Login successful!");
                    setTimeout(() => { window.location.href = "prof.html"; }, 1000);

                } else {
                    showMessage(data.message);
                }

            } catch(err) {
                showMessage("Network Error: " + err.message);
            }
        });
    }

}); // نهاية DOMContentLoaded

// --- Toggle UI ---
const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

if (registerBtn) {
    registerBtn.addEventListener('click', () => {
        if (container) container.classList.add('active');
    });
}

if (loginBtn) {
    loginBtn.addEventListener('click', () => {
        if (container) container.classList.remove('active');
    });
}