var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    //ignore this for now
    var enumerate = function(v) {
        var k=0;
        return v.map(function(e) {e._idx = k++;});
    };

    //gets the users for an org
    self.get_users = function (orgid){
        $.getJSON('/getusersinorg/' + orgid)
                .then(function(response){
                 self.users = response;
                 console.log(response);
                 console.log(self.users);
                });
    };

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            users: []
        },
        methods: {
            get_users: self.get_users,
        }

    });

    // i dont know how to pass this orgid on start up
    //self.get_users(orgid);

    $("#vue-div").show();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
