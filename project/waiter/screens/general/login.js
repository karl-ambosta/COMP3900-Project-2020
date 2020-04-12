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
                    // token = sessionStorage.getItem('token')
                    var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
                    axios.defaults.headers.common['Authorization'] = basicAuth

                    if(this.username == 'admin' && this.password == 'admin') {
                        this.adminLogin();
                    } else if(this.username == 'cashier' && this.password == 'cashier1') {
                        this.cashierLogin();
                    } else if(this.username == 'kitchen' && this.password == 'kitchenstaff') {
                        this.kitchenLogin();
                    } else if(this.username == 'waiter' && this.password == 'waiter12') {
                        this.waiterLogin();
                    } else {
                        this.customerLogin();
                    }
                }).catch( error => { 
                    document.getElementById('errorMessage').textContent = "Please enter the correct login details" 
                });
        },
        customerLogin() {
            window.open("../customer/customer.html", "_self");
        },
        kitchenLogin() {
            window.open("../kitchen-staff/kitchen_final.html", "_self")
        },
        cashierLogin() {
            window.open("../cashier/cashiers_final.html", "_self")
        },
        waiterLogin() {
            window.open("../waiter/waiters_final.html", "_self")
        },
        adminLogin() {
            window.open("../admin/dashboard.html", "_self")
        },
        goBack: function() {
            console.log("Here")
            window.open("landing_page.html", "_self");
        }
    }
});
