var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    //user object to store the data, this might not be neccassary
    function usersobject(firstName, lastName, email, id) {
        this.first_name =  firstName;
        //console.log(this.first_name);
        this.last_name = lastName;
        //console.log(this.last_name);
        this.email = email;
        //console.log(this.email);
        this.id = id;
    };

    function positionsobject(t, o){
        this.title = t;
        this.orgid = o;
    }

    //function to add the user data to the user object
    function adduserstoarray(response) {
        console.log('addusertoarray was called');

        for (var i = 0; i < response.length; i++) {
            console.log(response[i].first_name)
            first = response[i].first_name;
            last = response[i].last_name;
            email = response[i].email;
            id = response[i].id;
            APP.vue.adduser(
                new usersobject(first, last, email, id)
            );
        }
    }

    function addpositionstoarray(response) {
        console.log('addpositionstoarray was called');
        for (key in response)   {
            t = response[key].title;
            o = response[key].orgid;
            APP.vue.addposition(
                    new positionsobject(t, o)
                );
        }
    }

    //function to add the user object to the vue array
    self.adduser = function (u) {
        console.log('adduser called ' + u);
        APP.vue.users.push(u);
    }

    self.addposition = function(p){
        console.log('addposition called' + p);
        APP.vue.positions.push(p);
    }

    //gets the users for an org
    self.get_users = function (){
        $.getJSON('/getusersinorg/' + orgid)
                .then(function(response){
                    //clear the array of users
                    APP.vue.users = [];
                    adduserstoarray(response);
                });
    };

    self.get_positions = function(){
        $.getJSON('/getpositionsinorg/' + orgid)
                .then(function(response){
                    APP.vue.positions = [];
                    addpositionstoarray(response);
                });
    };

    // functions for when a user is clicked from the drawer
    self.memberDetail = function(index) {
        member = self.vue.users[index];
        $('#memberDetailTitle').html(member.first_name + " " + member.last_name);
        $('#memberDetailFirstName').html(member.first_name);
        $('#memberDetailLastName').html(member.first_name);
        $('#memberDetailEmail').html(member.email);
        $('#memberDetailId').html(member.id);
        $('#memberDetailModal').modal('show');
    }

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
            adduser: self.adduser,
            get_positions: self.get_positions,
            addposition: self.addposition,
            member_detail: self.memberDetail
        }

    });

    // i dont know how to pass this orgid on start up
    self.get_users();
    self.get_positions();
    $("#vue-div").show();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
