var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    //user object to store the users.
    function usersobject(firstName, lastName, email, id) {
        this.first_name =  firstName;
        this.last_name = lastName;
        this.email = email;
        this.id = id;
    };

    //position object to store the positions.
    function positionsobject(t, o, p, d){
        this.title = t;
        this.orgid = o;
        this.id = p;
        this.description = d;
    }

    //object to store the positions assigned to a user.
    function assignedpositionobject(t, p){
        this.title = t;
        this.id = p;
    }

    //object to store the users assigned to a position.
    function assigneduserobject(f, l, i){
        this.first_name = f;
        this.last_name = l;
        this.id = i;
    }

    //function to add the user data to the user object
    function adduserstoarray(response) {
        for (var i = 0; i < response.length; i++) {
            first = response[i].first_name;
            last = response[i].last_name;
            email = response[i].email;
            id = response[i].id;
            APP.vue.adduser(
                new usersobject(first, last, email, id)
            );
        }
    }

    //function to add the position data to the position object
    function addpositionstoarray(response) {
        for (key in response)   {
            t = response[key].title;
            o = response[key].orgid;
            p = response[key].id;
            d = response[key].description;
            APP.vue.addposition(
                    new positionsobject(t, o, p, d)
                );
        }
    }

    //function to add the position data to the assignedposition object
    function addassignedpositiontoarray(response){
        for (var i = 0; i < response.length; i++) {
            title = response[i].title;
            posid = response[i].position_id;
            userid = response[i].user_id;
            APP.vue.addassignedposition(
                new assignedpositionobject(title, posid)
            );
        }
    }

    //function to add the user data to the assigneduser object
    function addassigneduserstoarray(response){
        for(var i=0; i<response.length; i++){
            first_name = response[i].first_name;
            last_name = response[i].last_name;
            id = response[i].id;
            APP.vue.addassigneduser(
                new assigneduserobject(first_name, last_name, id)
            );
        }
    }

    //function to add the user object to the vue array
    self.adduser = function (u) {
        APP.vue.users.push(u);
    }

    //function to add the position object to the vue array
    self.addposition = function(p){
        APP.vue.positions.push(p);
    }

    //function to add the assignedposition object to the vue array
    self.addassignedposition = function(ap){
        APP.vue.assignedpositions.push(ap);
    }

    //function to add the assigneduser object to the vue array
    self.addassigneduser = function(au){
        APP.vue.assignedusers.push(au);
    }

    //gets the users for an organization
    self.get_users = function (){
        $.getJSON('/getusersinorg/' + orgid)
                .then(function(response){
                    APP.vue.users = [];         //this clear the array of users
                    adduserstoarray(response);
                });
    };

    //gets the positions for an organization
    self.get_positions = function(){
        $.getJSON('/getpositionsinorg/' + orgid)
                .then(function(response){
                    APP.vue.positions = [];
                    addpositionstoarray(response);
                });
    };

    //gets the positions assigned to a user
    self.get_assigned_positions = function(index){
        memberid = APP.vue.userid;
        $.getJSON('/getassignedpositions/' + orgid + '/' + memberid)
            .then(function(response){
                APP.vue.assignedpositions = [];
                addassignedpositiontoarray(response);
            })
    }

    //gets the users assigned to a position
    self.get_assigned_users = function(index){
        pos = APP.vue.posid;
        $.getJSON('/getpositionmembers/' + pos )
            .then(function(response){
                APP.vue.assignedusers = [];
                addassigneduserstoarray(response);
            })
    }

    // functions for when a user is clicked from the drawer
    self.memberDetail = function(index) {
        member = self.vue.users[index];
        $('#memberDetailTitle').html(member.first_name + " " + member.last_name);
        $('#memberDetailFirstName').html(member.first_name);
        $('#memberDetailFirstName2').html(member.first_name);
        $('#memberDetailFirstName3').html(member.first_name);
        $('#memberDetailLastName').html(member.last_name);
        $('#memberDetailEmail').html(member.email);
        $('#memberDetailId').html(member.id);
        
        $.getJSON('/getmembership/' + orgid + '/' + member.id)
            .then(function(response){
                APP.vue.curr_membership_id = response.id;
                APP.vue.curr_membership_admin = response.is_admin;
                $('#memberDetailAdmin').html(response.is_admin);
            });
            
        APP.vue.userid = member.id;

        self.get_assigned_positions(index);

        $('#memberDetailModal').modal('show');
    }

    // functions for when a position is clicked from the drawer
    self.positionDetail = function(index) {
        position = self.vue.positions[index];
        $('#positionDetailTitle').html(position.title);
        $('#positionDetailTitle1').html(position.title);
        $('#positionDetailTitle2').html(position.title);
        $('#positionDetailTitle3').html(position.title);
        $('#positionDetailDescription').html(position.description);
        $('#positionDetailId').html(position.id);

        APP.vue.posid = position.id;

        self.get_assigned_users(index);

        $('#positionDetailModal').modal('show');
    }

    //unassigns a user from a position 
    self.unassign_position = function(index){
        var uid = APP.vue.userid;
        var posid = self.vue.assignedpositions[index].id;

        url = "/unassign/" + uid.toString() + "/" + posid.toString()

        $.post(url,
            function () {
                self.get_assigned_positions();
            });
    }

    //unassigns a position from a user 
    self.unassign_user = function(index){
        var posid = APP.vue.posid;
        var userid = self.vue.assignedusers[index].id;

        url = "/unassign/" + userid.toString() + "/" + posid.toString()

        $.post(url,
            function () {
                self.get_assigned_users();
            });
    }

    //sets a user to admin
    self.set_admin = function(){
        var mid = APP.vue.curr_membership_id;

        url = '/setadmin/' + mid.toString()

        $.post(url);
    }


    // Vue Object
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            users: [],
            positions: [],
            assignedpositions: [],
            assignedusers: [],
            orgid: orgid,
            userid: -1,
            posid: -1,
            curr_membership_id: 0,
            curr_membership_admin: false
        },
        methods: {
            get_users: self.get_users,
            adduser: self.adduser,
            get_positions: self.get_positions,
            addposition: self.addposition,
            position_detail: self.positionDetail,
            member_detail: self.memberDetail,
            get_assigned_positions: self.get_assigned_positions,
            get_assigned_users: self.get_assigned_users,
            addassignedposition: self.addassignedposition,
            addassigneduser: self.addassigneduser,
            unassign_position: self.unassign_position,
            unassign_user: self.unassign_user,
            assign_user: self.assign_user,
            set_admin: self.set_admin
        }

    });

    self.get_users();
    self.get_positions();
    $("#vue-div").show();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
