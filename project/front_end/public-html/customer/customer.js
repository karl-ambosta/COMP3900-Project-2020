function viewOrderInfo() {
    window.open("order_info.html", "_self");
}

function finishOrdering() {
    window.open("billing.html", "_self");
}

function callWaiter() {
    // To call waiter
}

var titleApp = new Vue ({
    el: '#titleApp',
    delimiters: ['{{', '}}'],
    data: {
        userName: '',
        restaurant: '',
        tableNo: ''
    },
    created() {
        this.user = sessionStorage.getItem('user')
        this.restaurant = JSON.parse(sessionStorage.restaurant);
        this.tableNo = sessionStorage.getItem('tableNo')
    }
})

var orderApp = new Vue({
    el: '#orderApp',
    delimiters: ['{{', '}}'],
    data: {
        // get list of orders here
        user: '',
        orderList: [
            // List of customer orders
            // { id, owner, order_request: [] }
            {id: '00001', items: [ 
                                    { name: 'Item 1', description: 'Description for Item1', price: '2.50'}, 
                                    { name: 'Item 3', description: 'Description for Item3', price: '5.50'}  
                                ],
                time: '13:40', status: 'Completed'
            },
            {id: '00002', items: [ 
                                    { name: 'Item 2', description: 'Description for Item2', price: '10.00'}, 
                                    { name: 'Item 4', description: 'Description for Item4', price: '3.00'}  
                                ],
                time: '14:00', status: 'Cooking'
            },
        ],
        currentOrder: [
            // List of Menu Items
            // item = id, name, quantity, comments
        ],
        restaurant: ''
    },
    created() {
        var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
        axios.defaults.headers.common['Authorization'] = basicAuth

        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/orderList/')
            .then((response) => {
                this.orderList = response.data
            }).catch( error => {console.log(error); return});

        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/restaurant/')
            .then((response) => {
                for(i = 0; i < response.data.length; i++) {
                    if(response.data[i].name == sessionStorage.getItem('restaurant')) {
                        this.restaurant = response.data[i]
                    }
                }
            }).catch( error => {console.log(error); return });
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
        viewOrderInfo: function(orderID) {
            sessionStorage.orderID = orderID
        },
        updateOrderNo: function(orderID) {
            infoApp.order.id = orderID
        },
        sendOrder: function() {

            if(this.currentOrder.length < 1) {
                document.getElementById("orderMessage").style.color = "red"
                document.getElementById("orderMessage").textContent = "Cannot send an empty order, try adding some items to your order"
                return;
            }

            /*
            axios
            .post('https://api.unswcafe.tuesdaywaiter.tk/orderList/', null)
            .then((response) => {
                newOrder = response.data
                sessionStorage.orderID = newOrder.id
            }).catch( error => {console.log(error); return});


            for(i = 0; i < this.currentOrder.length; i++) {
                order = this.currentOrder[i]
                
                axios
                .post('https://api.unswcafe.tuesdaywaiter.tk/menuItems/' + order.id + '/order/', {comment: order.comment, quantity: Number(order.quantity)})
                .then((response) => {
                    console.log(response.data)
                }).catch( error => {console.log(error); return});
            }

            */

            this.currentOrder = ''
            document.getElementById("orderMessage").style.color = "green"
            document.getElementById("orderMessage").textContent = "Order successfully sent!"
        },
        orderTotals: function() {
            var total = 0

            for(i = 0; i < this.currentOrder.length; i++) {
                total = total + (Number(this.currentOrder[i].price) * Number(this.currentOrder[i].quantity))
            }

            return total.toFixed(2)
        },
    }

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
            .get('https://api.unswcafe.tuesdaywaiter.tk/menuItems/')
            .then((response) => {
                this.items = response.data
            }).catch( error => {console.log(error); });
            
        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/menuCategories/')
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
            // console.log({ itemName: this.itemName, quantity: this.quantity, comment: this.comment })
        },
        processForm: function() {
            // send input to database
            // POST { orderList object, menuItem object, comments, quantity}

            idx = this.items.findIndex(x => x.name == this.itemName)
            item = this.items[idx]
            
            orderApp.currentOrder.push({ id: item.id, itemName: this.itemName, quantity: this.quantity, comment: this.comment, price: item.price });

            console.log(orderApp.currentOrder)

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
            {id: '00003', orderTime: "13:40", status: "Serving", itemList: [
                                                        {itemName: "item1", description: "Description for item1", quantity: 1, notes: "Please make fresh", price: 2.50},
                                                        {itemName: "item2", description: "Description for item2", quantity: 2, notes: "Remove tomatoes", price: 5.50},
                                                        {itemName: "item3", description: "Description for item3", quantity: 2, notes: "No peanuts", price: 7.00},
                                                        {itemName: "item4", description: "Description for item4", quantity: 6, notes: "Extra chilli", price: 3.50},
                                                        ]}
        ]
        
        /*
        orderNumber: "00003",
        orderTime: "13:40",
        status: "Cooking",
        itemList: [
            {itemName: "item1", description: "Description for item1", quantity: 1, notes: "Please make fresh", price: 2.50},
            {itemName: "item2", description: "Description for item2", quantity: 2, notes: "Remove tomatoes", price: 5.50},
            {itemName: "item3", description: "Description for item3", quantity: 2, notes: "No peanuts", price: 7.00},
            {itemName: "item4", description: "Description for item4", quantity: 6, notes: "Extra chilli", price: 3.50},
        ]
        */
    },
    /*
    created() {
        var basicAuth = 'Basic ' + sessionStorage.getItem('btoa')
        axios.defaults.headers.common['Authorization'] = basicAuth
        
        axios
            .get('https://api.unswcafe.tuesdaywaiter.tk/orderList/' + sessionStorage.getItem('orderID'))
            .then((response) => {
                this.order = response.data
            }).catch( error => {console.log(error); })
        
    },
    */
    computed: {
        getTimes: function() {
            var time = moment(this.order[0].orderTime, "HH:mm")
            var timeFormat = time.format('hh:mm A')
            var expectedTime = time.add(10, 'minutes').format('hh:mm A')
            return [timeFormat, expectedTime];
        },
        orderTotals: function() {
            var total = 0
            for(i = 0; i < this.order[0].itemList.length; i++) {
                total = total + (this.order[0].itemList[i].price * this.order[0].itemList[i].quantity)
            }

            return total
        }
    },
    methods: {
        processForm: function() {
            // send input to database
              console.log({ name: this.custName, restaurant: this.restaurant, table_no: this.table_no, email: this.email, mobile: this.mobile });
        }
    }

})