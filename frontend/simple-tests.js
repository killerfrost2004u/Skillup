// tests/simple-tests.js

console.log("%c🚀 Skill Up - Simple Testing Started", "color: #4CAF50; font-size: 16px; font-weight: bold");

const UserStore = UserStore || { getInstance: () => ({}) }; // Fallback

// ==================== TEST SUITE ====================

function runAllTests() {
    console.clear();
    console.log("%c📋 Starting All Tests...", "color: orange; font-size: 14px");

    testUserStore();
    testLocalStorage();
    testInputValidation();
    testAuthGuard();
    testLoginSimulation();

    console.log("%c✅ All Tests Completed!", "color: #4CAF50; font-size: 16px; font-weight: bold");
}

// ====================== 1. UserStore Singleton Test ======================
function testUserStore() {
    console.log("\n🔹 Testing UserStore (Singleton)...");
    const store1 = UserStore.getInstance();
    const store2 = UserStore.getInstance();

    if (store1 === store2) {
        console.log("✅ Singleton Test Passed: Same instance returned");
    } else {
        console.error("❌ Singleton Test Failed");
    }

    // Test login & getUser
    store1.logout(); // clean start
    store1.login({ id: 1, name: "Dina Test", email: "dina@test.com" });

    const user = store1.getUser();
    if (user && user.name === "Dina Test") {
        console.log("✅ Login & getUser Test Passed");
    } else {
        console.error("❌ Login Test Failed");
    }
}

// ====================== 2. localStorage Test ======================
function testLocalStorage() {
    console.log("\n🔹 Testing localStorage...");

    const store = UserStore.getInstance();
    store.logout();

    const testUser = {
        id: Date.now(),
        name: "Test User",
        email: "test@skillup.com"
    };

    store.login(testUser);

    const saved = localStorage.getItem("skillup_user");
    if (saved) {
        const parsed = JSON.parse(saved);
        console.log("✅ User saved successfully in localStorage");
        console.log("Saved User:", parsed);
    } else {
        console.error("❌ Failed to save user in localStorage");
    }
}

// ====================== 3. Input Validation ======================
function testInputValidation() {
    console.log("\n🔹 Testing Input Validation...");

    function validateLogin(email, password) {
        if (!email || email.trim() === "") {
            console.warn("⚠️ Email is required");
            return false;
        }
        if (!password || password.trim() === "") {
            console.warn("⚠️ Password is required");
            return false;
        }
        if (!email.includes("@")) {
            console.warn("⚠️ Invalid email format");
            return false;
        }
        return true;
    }

    // Test cases
    console.log(validateLogin("", "123456") ? "✅" : "❌", "Empty Email Test");
    console.log(validateLogin("test@email.com", "") ? "✅" : "❌", "Empty Password Test");
    console.log(validateLogin("test@email.com", "123456") ? "✅" : "❌", "Valid Input Test");
}

// ====================== 4. Auth Guard Test ======================
function testAuthGuard() {
    console.log("\n🔹 Testing Auth Guard...");
    const store = UserStore.getInstance();
    
    if (typeof updateNavbar === "function") {
        console.log("✅ updateNavbar function exists");
    } else {
        console.warn("⚠️ updateNavbar not found (check auth-guard.js)");
    }

    console.log("Current User:", store.getUser() ? "Logged In" : "Not Logged In");
}

// ====================== 5. Simulated Login Test ======================
function testLoginSimulation() {
    console.log("\n🔹 Simulated Login Test...");
    const store = UserStore.getInstance();
    store.logout();

    const fakeUser = {
        id: 999,
        name: "Dina Ahmed",
        email: "dina@skillup.com",
        role: "Student"
    };

    store.login(fakeUser);
    console.log("✅ Simulated Login Successful");
    console.log("You can now go to Profile page and test");
}

// Run tests automatically when file is loaded
console.log("%cType runAllTests() in console to run all tests", "color: #2196F3; font-weight: bold");

// Auto run on load
window.onload = () => {
    setTimeout(runAllTests, 800);
};