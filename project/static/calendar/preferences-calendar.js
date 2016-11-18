$(document).ready(function() {
    var timeId = 1;

    //Retrieve list of events for current_user
    $.ajax({
        url: 'getTwitterFollowers.php',
        type: 'GET',
        data: 'twitterUsername=jquery4u',
        success: function(data) {
            //called when successful
            $('#ajaxphp-results').html(data);
        },
        error: function(e) {
            //called when there is an error
            //console.log(e.message);
        }
    });

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        defaultView: 'agendaWeek',
        allDaySlot: false,
        editable: true,
        selectable: true,
        selectHelper: true,

        select: function(start, end, allDay) {
            var newEvent = {
                start: start,
                end: end,
                id: timeId,
            };
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            timeId = timeId + 1;
            
            var newEventString = JSON.stringify(newEvent);

            console.log("String output:  " + newEventString);
            console.log("Object output:  " + newEvent);
 
            $.ajax({
                url: "/updatepreferences",
                type: "POST",
                data: newEventString,
                dataType: 'json',
                success: function(data) {
                    alert("Totes worked: " + newEventString);
                }
            });
            
            /*Test Code to convert event to string back to event
            var backtoObject = JSON.parse(newEventString);
            console.log("backToMoment:  " + backtoObject);
            console.log("restringed:  " + JSON.stringify(backtoObject)); */

        },

        eventClick: function (calEvent, jsEvent, view) {           
            $('#calendar').fullCalendar('removeEvents', calEvent._id);
            var calEventOutput = {
                start: calEvent.start,
                end: calEvent.end,
                id: calEvent.id,
            }
            console.log("calEventStringg:  " + JSON.stringify(calEventOutput));

            $.ajax({
                url: "/updatepreferences/delete",
                type: "POST",
                data: JSON.stringify(calEventOutput),
                dataType: 'json',
                success: function(data) {
                    alert("Totes worked: " + newEventString);
                }
            });

        }
    });


    /*
    *
    * Code to Create new Position
    *
    */

    /*
    $('#inviteMemberSubmit').on('click', function() {
        var newUser = {
            first_name: $('#first_name').val(),
            last_name: $('#last_name').val(),
            email: $('#email').val()
        };



        url = "/profile"

        $.ajax({
            type: "POST",
            url: url,
            data: $("#inviteMemberForm").serialize(), // serializes the form's elements.

            success: function(data)
            {

                if(data.status == "success"){
                    APP.adduser(newUser);
                    $('#inviteMemberModal').modal('hide');
                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                }
            }
        });
    }); */

});