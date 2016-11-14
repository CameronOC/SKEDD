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

    function positionsobject(t, o, p){
        this.title = t;
        this.orgid = o;
        this.id = p;
    }

    function assignedpositionobject(t, p){
        this.title = t;
        this.id = p;
    }

    //function to add the user data to the user object
    function adduserstoarray(response) {
        console.log('addusertoarray was called');

        for (var i = 0; i < response.length; i++) {
            //console.log(response[i].first_name)
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
            p = response[key].id;
            APP.vue.addposition(
                    new positionsobject(t, o, p)
                );
        }
    }

    function addassignedpositiontoarray(response){
        console.log('addassignedpositiontoarray was called');
        //console.log(response);
        for (var i = 0; i < response.length; i++) {
            //console.log(response[i].title)
            title = response[i].title;
            posid = response[i].position_id;
            userid = response[i].user_id;
            APP.vue.addassignedposition(
                new assignedpositionobject(title, posid)
            );
        }
    }

    //function to add the user object to the vue array
    self.adduser = function (u) {
        //console.log('adduser called ' + u);
        APP.vue.users.push(u);
    }

    self.addposition = function(p){
        //console.log('addposition called' + p);
        APP.vue.positions.push(p);
    }

    self.addassignedposition = function(ap){
        //console.log('add assignedposition called' + ap);
        APP.vue.assignedpositions.push(ap);
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

    self.get_assigned_positions = function(index){
        //member = self.vue.users[index];
        //console.log(member)
        memberid = APP.vue.userid;
        //console.log(memberid);
        $.getJSON('/getassignedpositions/' + orgid + '/' + memberid)
            .then(function(response){
                APP.vue.assignedpositions = [];
                addassignedpositiontoarray(response);
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

        APP.vue.userid = member.id;
        //console.log(member.id);

        self.get_assigned_positions(index);

        $('#memberDetailModal').modal('show');
    }

    self.unassign_position = function(index){

        console.log("unassign_position called")

        var uid = APP.vue.userid;
        var posid = self.vue.assignedpositions[index].id;
        console.log(posid);

        url = "/unassign/" + uid.toString() + "/" + posid.toString()

        $.post(url,
            function () {
                self.get_assigned_positions();
            });
    }

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            users: [],
            positions: [],
            assignedpositions: [],
            orgid: orgid,
            userid: -1
        },
        methods: {
            get_users: self.get_users,
            adduser: self.adduser,
            get_positions: self.get_positions,
            addposition: self.addposition,
            member_detail: self.memberDetail,
            get_assigned_positions: self.get_assigned_positions,
            addassignedposition: self.addassignedposition,
            unassign_position: self.unassign_position
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
