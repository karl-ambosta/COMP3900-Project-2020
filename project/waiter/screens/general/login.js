
var app = new Vue({
    el: '#app',
    delimiters: ['{{', '}}'],
    data: {
        username: '',
        email: '',
        password: '',
        results: 'start'
    },
    methods: {
        login () {
            console.log("login with: username: <" + this.username + "> and password: <" + this.password + ">")
            var proxyURL = 'https://cors-anywhere.herokuapp.com/'
            var apiURL = 'http://127.0.0.1:8000/rest-auth/login/'

            var payload = {
                username: this.username,
                password: this.password,
            };

            axios
                .post(apiURL, payload)
                .then((response) => {
                    this.results = response.data.results;
                    console.log(response.data.key)
                  }).catch( error => { console.log(error); });
            
        }
    }
});
