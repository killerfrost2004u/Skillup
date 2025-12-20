document.addEventListener('DOMContentLoaded', () => {

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
 // ----------- REGISTER -----------
if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("register-username").value;
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;

        try {
            const res = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password })
            });

            const data = await res.json(); // اقرأ body مرة واحدة فقط

            if(res.ok){
                // حفظ البيانات في localStorage مثل login
                localStorage.setItem('user', JSON.stringify({
                    user_id: data.user_id || null,
                    name: data.name || username,
                    email: data.email || email,
                    profile_image: data.profile_image || "user.jpg",
                    age: data.age || 20,
                    year: data.year || "Year",
                    major: data.major || "Computer",
                    college: data.college || "College"
                }));

                showMessage("Registered successfully!");
                setTimeout(() => { window.location.href = "SKILL UP.html"; }, 1000);
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
                const res = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });


                const data = await res.json(); // اقرأ body مرة واحدة فقط
                if(res.ok){
                    localStorage.setItem("user", JSON.stringify({
                        user_id:data.user_id,
                        name: data.name,
                        email: data.email,
                        profile_image: data.profile_image || "user.jpg",
                        age: data.age,
                        year: data.year,
                        major: data.major,
                        college: data.college
                    }));
                    showMessage("Login successful!");
                    setTimeout(() => { window.location.href = "SKILL UP.html"; }, 1000);




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
registerBtn.addEventListener('click', () => container.classList.add('active'));
loginBtn.addEventListener('click', () => container.classList.remove('active'));

