const UserStore = (function () {

    let currentUser = null;

    function load() {
        const saved = localStorage.getItem("skillup_user");
        if (saved) {
            currentUser = JSON.parse(saved);
        }
    }

    load();

    return {
        login: function (user) {
            currentUser = user;
            localStorage.setItem("skillup_user", JSON.stringify(user));
            console.log("USER SAVED ✔", user);
        },

        getUser: function () {
            return currentUser;
        }
    };

})();