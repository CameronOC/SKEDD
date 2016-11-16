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
            var newEventData = {from: start.format('dddd, hh:mm a'), to: end.format('dddd, hh:mm a'), id: timeId};
            var newEvent = {
                start: start,
                end: end,
                id: timeId,
            };
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            timeId = timeId + 1;
            alert('EVENT ID:  '+newEventData.id+' || '+'START:  '+newEventData.from+' || '+'END:  '+newEventData.to);
            
            var newEventDataString = JSON.stringify(newEventData);

            alert(newEventDataString);


            $.ajax({
                url: "/profile",
                type: "POST",
                data: {
                newEventDataString
                },
                dataType: "json",
                success: function(data) {
                    alert("Data: " + newEventDataString);
                },
                error: function(data){
                    alert("Shit Failed:  " + newEventDataString);
                }
            });

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