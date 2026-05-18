const UserStore = (function () {

    let user = null;

    return {
        setUser: function (data) {
            user = data;
        },

        getUser: function () {
            return user;
        }
    };

})();