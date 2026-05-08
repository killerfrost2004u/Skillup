// frontend/auth-guard.js
const API_BASE_URL = window.location.origin === 'http://127.0.0.1:5500' || window.location.origin === 'http://localhost:5500' ? 'http://127.0.0.1:5000' : '';

// 1. Check if user is logged in locally
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

// 2. Protect Page (Redirect if not logged in)
async function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = "log.html?show=register";
        return;
    }
    // Optional: Validate token with server on load
    try {
        const response = await fetch(`${API_BASE_URL}/api/check-auth`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (!data.authenticated) handleLogout();
    } catch (error) {
        console.error("Auth check error:", error);
    }
}

// 3. Helper: Fetch Data with "Authorization" Header
// Use this function instead of normal fetch() for protected content!
async function fetchWithAuth(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.error("No token found!");
        return null;
    }

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...(options.headers || {}) // Merge any other headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: headers
        });

        // If token is expired (401), force logout
        if (response.status === 401) {
            handleLogout();
            return null;
        }

        return response;
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}

// 4. Logout Function
function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userCourses'); 
    localStorage.removeItem('userNotes');
    localStorage.removeItem('userProgress');
    window.location.href = "log.html?show=register";
}