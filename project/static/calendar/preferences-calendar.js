$(document).ready(function() {
    var timeId = 0;

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