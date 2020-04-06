

var app = new Vue({
    el: '#app',
    delimiters: ['{{', '}}'],
    data: {
        username: '',
        email: '',
        password: ''
    },
    methods: {
        login () {
            console.log("login with: username: <" + this.username + "> and password: <" + this.password + ">")
            var proxyURL = 'https://cors-anywhere.herokuapp.com/'
            var apiURL = 'http://127.0.0.1:8000/rest-auth/login/'

            var data = {
                username: this.username,
                password: this.password,
            };

            fetch(proxyURL+apiURL, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                  },
                body: JSON.stringify(data),
            })
            .then(function(res){ return res.json(); })
            .then(function(data){ alert( JSON.stringify( data ) ) })
            
            
        }
    }
});
