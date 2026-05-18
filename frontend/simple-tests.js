function runHomeTests() {
    console.log("🧪 HOME TESTING STARTED");

    // Test 1: user exists
    const user = JSON.parse(localStorage.getItem("skillup_user"));

    if (user) {
        console.log("✔ USER EXISTS:", user);
    } else {
        console.log("❌ NO USER FOUND");
    }

    // Test 2: welcome element exists
    const welcome = document.querySelector(".sub-text");

    if (welcome) {
        console.log("✔ WELCOME ELEMENT FOUND");
    } else {
        console.log("❌ WELCOME ELEMENT MISSING");
    }

    // Test 3: navbar exists
    const nav = document.querySelector(".navbar");

    if (nav) {
        console.log("✔ NAVBAR FOUND");
    } else {
        console.log("❌ NAVBAR MISSING");
    }

    console.log("🧪 HOME TESTING DONE");
}