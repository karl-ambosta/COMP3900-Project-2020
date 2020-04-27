var loginApp = new Vue({
    el: '#loginApp',
    delimiters: ['{{', '}}'],
    data: {
        username: '',
        email: '',
        password: '',
        results: 'start'
    },
    methods: {
        goBack: function() {
            console.log("Here")
            window.open("index.html", "_self");
        },
        async login () {
 
            var payload = {
                username: this.username,
                password: this.password,
            };

            await axios
                .post('http://127.0.0.1:8000/rest-auth/login/', payload)
                .then((response) => {
                    this.results = response.data.key;
                    sessionStorage.user = this.username
                    sessionStorage.btoa = btoa(this.username + ":" + this.password)

                    sessionStorage.setItem('restaurant', JSON.stringify(
                        { id: 1, name: 'UNSW Cafe'}
                    ));

                    var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
                    axios.defaults.headers.common['Authorization'] = basicAuth

                    axios
                        .get('http://127.0.0.1:8000/profile/')
                        .then((response) => {
                            userInfo = response.data.filter(x => x.username == this.username)[0]
                            console.log(userInfo)
                            if(userInfo.role == 1) { // user logged in is a customer
                                this.customerLogin(userInfo)
                            } else if(userInfo.role == 2) { // user logged in is a cashier
                                window.open("cashier.html", "_self")
                            } else if(userInfo.role == 3) { // user logged in is kitchen staff
                                window.open("kitchen.html", "_self")
                            } else if(userInfo.role == 4) { // user logged in is a manager
                                window.open("dashboard.html", "_self")
                            } else if(userInfo.role == 5) { // user logged in is a waiter
                                window.open("waiter.html", "_self")
                            }
                        }).catch( error => {console.log(error); return })
                }).catch( error => { 
                    document.getElementById('errorMessage').textContent = "Please enter the correct login details" 
                });
        },
        customerLogin(userProfile) {
            if(userProfile.first_name == "" || userProfile.last == "") {
                window.open("customer.html", "_self");
            } else {
                window.open("customer_orders.html", "_self");
            }
        }
    }
});

var registerApp = new Vue ({
    el: '#registerApp',
    delimiters: ['{{', '}}'],
    data: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        results: 'start'
    },
    methods: {
        async register() {

            l = this.password.length;

            if(this.password != this.confirmPassword) {
                document.getElementById('errorMessage2').textContent = "Passwords do not match!"
                return;
            } else if(l < 8) {
                document.getElementById('errorMessage2').textContent = "Password is too short. Must be at least 8 characters."
                return;
            }

            var details = {
                username: this.username,
                email: this.email,
                password1: this.password,
                password2: this.confirmPassword
            }

            await axios
                .post('http://127.0.0.1:8000/rest-auth/register/', details)
                .then((response) => {
                    console.log(response.data)
                    message = document.getElementById("errorMessage2")
                    message.textContent = "User has been successfully registered. Please login in!"
                    message.style.color = "greenyellow"

                    this.username = ''
                    this.email = ''
                    this.password = ''
                    this.confirmPassword = ''
                }).catch((error) => {
                    console.log(error);
                    message = document.getElementById("errorMessage2")
                    message.textContent = "Cannot register user!"
                    message.style.color = "greenyellow"

                    this.password = ''
                    this.confirmPassword = ''
                });

            
        }
    }
})
