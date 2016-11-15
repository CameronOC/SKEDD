$(document).ready(function() {
    var nextId = 0;

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
            var s = start.format('dddd, hh:mm a');
            var e = end.format('dddd, hh:mm a');
            var newEvent = {
                start: start,
                end: end,
                id: nextId,
            };
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            nextId = nextId + 1;
            alert('EVENT ID:  '+newEvent.id+' || '+'START:  '+s+' || '+'END:  '+e);
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

    $('#inviteMemberSubmit').on('click', function() {
        var newUser = {
            first_name: $('#first_name').val(),
            last_name: $('#last_name').val(),
            email: $('#email').val()
        };



        url = "/organization/" + orgid.toString() + "/invite"



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
    });

});