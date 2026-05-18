function runHomeTests() {
    console.log("🧪 HOME TEST START");

    const user = JSON.parse(localStorage.getItem("skillup_user"));

    if (user) {
        console.log("✔ USER FOUND:", user);
    } else {
        console.log("❌ USER NOT FOUND");
    }

    const nav = document.querySelector(".navbar");
    console.log(nav ? "✔ NAVBAR OK" : "❌ NAVBAR MISSING");

    const welcome = document.querySelector(".sub-text");
    console.log(welcome ? "✔ WELCOME OK" : "❌ WELCOME MISSING");

    console.log("🧪 HOME TEST END");
}

document.addEventListener("DOMContentLoaded", runHomeTests);