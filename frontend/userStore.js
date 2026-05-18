// userStore.js ===========================================
const UserStore = (function () {
    let instance;

    function createInstance() {
        let currentUser = null;

        // Load from localStorage when created
        function loadUser() {
            const saved = localStorage.getItem("skillup_user");
            if (saved) {
                currentUser = JSON.parse(saved);
            }
        }

        loadUser();

        return {
            login: function (userData) {
                currentUser = userData;
                localStorage.setItem("skillup_user", JSON.stringify(userData));
                console.log("✅ User logged in:", userData);
            },

            logout: function () {
                currentUser = null;
                localStorage.removeItem("skillup_user");
                console.log("👋 User logged out");
            },

            getUser: function () {
                return currentUser;
            },

            isLoggedIn: function () {
                return currentUser !== null;
            },

            // For profile updates
            updateUser: function (newData) {
                if (currentUser) {
                    currentUser = { ...currentUser, ...newData };
                    localStorage.setItem("skillup_user", JSON.stringify(currentUser));
                }
            }
        };
    }

    return {
        getInstance: function () {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})();