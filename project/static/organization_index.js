var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    //user object to store the data, this might not be neccassary
    function usersobject(f, l, e) {
        this.first_name =  f;
        //console.log(this.first_name);
        this.last_name = l;
        //console.log(this.last_name);
        this.email = e;
        //console.log(this.email);
    };

    //function to add the user data to the user object
    function adduserstoarray(response) {
        console.log('addusertoarray was called');
        for (key in response)   {
            f = response[key].first_name;
            l = response[key].last_name;
            e = response[key].email;
            APP.vue.adduser(
                    new usersobject(f, l, e)
                );
        }
    }

    //function to add the user object to the vue array
    self.adduser = function (u) {
        console.log('adduser called ' + u);
        APP.vue.users.push(u);
    }

    //gets the users for an org
    self.get_users = function (){
        $.getJSON('/getusersinorg/' + orgid)
                .then(function(response){
                 adduserstoarray(response);
                });
    };

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            users: [],
            positions: [],
            orgid: orgid
        },
        methods: {
            get_users: self.get_users,
            adduser: self.adduser
        }

    });

    // i dont know how to pass this orgid on start up
    self.get_users();
    $("#vue-div").show();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
