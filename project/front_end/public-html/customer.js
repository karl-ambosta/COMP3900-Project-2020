var titleApp = new Vue ({
    el: '#titleApp',
    delimiters: ['{{', '}}'],
    data: {
        chosen_restaurant: '',
        chosen_table: '',
        restList: [],
        userName: '',
        restaurant: [ /* id, name, tableNo */]
    },
    created() {
        var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
        axios.defaults.headers.common['Authorization'] = basicAuth

        this.userName = sessionStorage.getItem('user')

        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/restaurant/')
            .then((response) => {
                this.restList = response.data
                document.getElementById('preModal').style.display = "block"
            }).catch( error => {console.log(error); return })
    },
    methods: {
        processForm: function() {
            if(this.chosen_restaurant == '') {
                message = document.getElementById('submitMessage')
                message.textContent = "Please fill out all fields"
            } else {
                rID = this.restList.filter(x => x.name == this.chosen_restaurant)[0].id
                sessionStorage.setItem('restaurant', JSON.stringify(
                    { id: rID, name: this.chosen_restaurant, tableNo: this.chosen_table}
                ));

                document.getElementById('preModal').style.display = "none"
                
                this.restaurant = JSON.parse(sessionStorage.restaurant)
            } 
        },
        finaliseOrders: function() {
            // set orders to finished

            window.open("billing.html", "_self")
        }
    }
})



var orderApp = new Vue({
    el: '#orderApp',
    delimiters: ['{{', '}}'],
    data: {
        // get list of orders here
        orderList: [
            // List of customer orders
            // { id, owner, order_request: [] }
        ],
        currentOrder: [
            // List of Menu Items
            // item = id, name, quantity, comments
        ],
        requestNo: [],
    },
    created() {
        var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
        axios.defaults.headers.common['Authorization'] = basicAuth

        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/orderList/')
            .then((response) => {
                this.orderList = response.data.filter(item => item.owner == titleApp.userName)
            }).catch( error => {console.log(error); return});

        this.updateData();
    },
    computed: {
        orderTotals: function() {
            var total = 0

            for(i = 0; i < this.currentOrder.length; i++) {
                total = total + (Number(this.currentOrder[i].price) * Number(this.currentOrder[i].quantity))
            }

            return total.toFixed(2)
        },
    },
    methods: {
        processForm: function() {
            // send input to database
              console.log({ name: this.custName, restaurant: this.restaurant, table_no: this.table_no, email: this.email, mobile: this.mobile });
        },
        convertTime: function(timeString) {
            var s = moment(timeString, "HH:mm A").format('hh:mm A')
            return s;
        },
        updateOrderInfo: function(orderID) {
            infoApp.order = this.orderList.filter(item => item.id == orderID)[0]
            
            sessionStorage.orderID = orderID

            axios
                .get('https://api.unswcafe.tuesdaywaiter.tk/orderRequest/', { params: {order_list: orderID }})
                .then((response) => {
                    infoApp.order.order_request = response.data
                }).catch(error => {console.log(error);})
        },
        sendOrder: function() {
            var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
            axios.defaults.headers.common['Authorization'] = basicAuth

            axios.defaults.headers.common['Content-Type'] = "text/html"

            rInfo = titleApp.restaurant

            if(this.currentOrder.length < 1) {
                document.getElementById("orderMessage").style.color = "red"
                document.getElementById("orderMessage").textContent = "Cannot send an empty order, try adding some items to your order"
                return;
            }

            axios
            .post('https://api.unswcafe.tuesdaywaiter.tk/orderList/', { restaurant: rInfo.id, table_number: Number(rInfo.tableNo), order_request: [], status: 1 } )
            .then((response) => {
                newOrder = response.data
                sessionStorage.orderID = newOrder.id

                for(i = 0; i < this.currentOrder.length; i++) {
                    order = this.currentOrder[i]
    
                    axios
                    .post('https://api.unswcafe.tuesdaywaiter.tk/menuItems/' + order.id + '/order/', { comment: order.comment, quantity: Number(order.quantity) } )
                    .then((response) => {
                        console.log(response.data)
                    }).catch( error => {console.log(error); 
                        if (error.response) {
                            /*
                            * The request was made and the server responded with a
                            * status code that falls out of the range of 2xx
                            */
                           console.log(error.response.data);
                           console.log(error.response.status);
                           console.log(error.response.headers);
                       } else if (error.request) {
                           /*
                           * The request was made but no response was received, `error.request`
                           * is an instance of XMLHttpRequest in the browser and an instance
                           * of http.ClientRequest in Node.js
                           */
                           console.log(error.request);
                       } else {
                           // Something happened in setting up the request and triggered an Error
                           console.log('Error', error.message);
                       }
                       console.log(error.config);return })
               }

            }).catch( error => {console.log(error); 
               if (error.response) {
                   /*
                   * The request was made and the server responded with a
                   * status code that falls out of the range of 2xx
                   */
                   console.log(error.response.data);
                   console.log(error.response.status);
                   console.log(error.response.headers);
               } else if (error.request) {
                   /*
                   * The request was made but no response was received, `error.request`
                   * is an instance of XMLHttpRequest in the browser and an instance
                   * of http.ClientRequest in Node.js
                   */
                   console.log(error.request);
               } else {
                   // Something happened in setting up the request and triggered an Error
                   console.log('Error', error.message);
               }
               console.log(error.config);return })

            console.log("r.id = " + rInfo.id + " tableNo = " + Number(rInfo.tableNo))

            this.currentOrder = ''
            document.getElementById("orderMessage").style.color = "green"
            document.getElementById("orderMessage").textContent = "Order successfully sent!"
        },
        getStatusName: function(statusID) {
            if(statusID == 2) {
                return 'Recieved'
            } else if(statusID == 3) {
                return 'Preparing'
            } else if(statusID == 4) {
                return 'Cooking'
            } else if(statusID == 5) {
                return 'Serving'
            } else if(statusID == 6) {
                return 'Completed'
            }
        },
        updateData: function() {
            // timer for auto update 
            setInterval(() => {

            axios
                .get('https://api.unswcafe.tuesdaywaiter.tk/orderList/')
                .then((response) => {
                    this.orderList = response.data.filter(item => item.owner == titleApp.userName)
                }).catch( error => {console.log(error); return});
                
            }, 5000)
        },   
    },
})

function hideTypes() {
    var x = document.getElementsByClassName("items");
    var i;
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
}

function filterType(attribute) {
    var c = attribute.getAttribute('value');
    if(c == "all") {
        showTypes();
        return;
    }
    hideTypes();
    document.getElementById(c).style.display = "block"
}

function showTypes() {
    var x = document.getElementsByClassName("items");
    var i;
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "block";
    }
}

var menuApp = new Vue({
    el: '#menuApp',
    delimiters: ['{{', '}}'],
    data: {
        itemName: '',
        quantity: 0,
        comment: '',
        items: [
            // List of Menu Items
            // id, name, description, price, category, restaurant
        ],
        types: [
            // List of Menu Categories
            // type = { id, name, menu_item[] }
        ],
    },
    created() {
        var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
        axios.defaults.headers.common['Authorization'] = basicAuth
        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/menuItems/', { params: { restaurant: titleApp.restaurant.id }})
            .then((response) => {
                this.items = response.data
            }).catch( error => {console.log(error); });
            
        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/menuCategories/', { params: {restaurant: titleApp.restaurant.id }})
            .then((response) => {
                this.types = response.data
            }).catch(error => {console.log(error);})
    },
    computed: {
        getRestaurantID: function() {
            return titleApp.restaurant.id
        },
        resetFields: function() {
            this.quantity = ''
            this.comment = ''
            this.itemName = ''
        }
    },
    methods: {
        itemsOfType: function(typeID) {
            return this.items.filter(function(item) {
                if(item.menu_category == typeID) {
                    return item;
                };
            })
        },
        getItem: function(name) {
            for(i=0; i< this.items.length; i++) {
                if(this.items[i] == name) {
                    return this.items[i]
                }
            }
        },
        updateItemDetails: function(itemName) {
            if(itemName != null) {
                this.itemName = itemName
            }
        },
        processForm: function() {
            // send input to database
            // POST { orderList object, menuItem object, comments, quantity}
            idx = this.items.findIndex(x => x.name == this.itemName)
            item = this.items[idx]
            
            orderApp.currentOrder.push({ id: item.id, itemName: this.itemName, quantity: this.quantity, comment: this.comment, price: item.price });

            this.resetFields            
        }			
    }
  });

var infoApp = new Vue({
    el: '#infoApp',
    delimiters: ['{{', '}}'],
    data: {
        order: [
            // id, status, order_request
            
        ]
    },
    computed: {
        orderTotals: function() {
            var total = 0
            for(i = 0; i < this.order[0].itemList.length; i++) {
                total = total + (this.order[0].itemList[i].price * this.order[0].itemList[i].quantity)
            }

            return total
        }
    },
    methods: {
        getItemName: function(itemID) {
            return menuApp.items.filter(x => x.id == itemID)[0].name  
        },
        convertTime: function(timeString) {
            var s = moment(timeString, "HH:mm A").format('hh:mm A')
            return s;
        },
    },
})